"""Reproducible QLoRA pilot: baseline, train, then evaluate same fixed contexts."""
import argparse,json,time,hashlib,random
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM,BitsAndBytesConfig
from peft import LoraConfig,get_peft_model,prepare_model_for_kbit_training,PeftModel
ROOT=Path(__file__).resolve().parent
SYSTEM='Bạn trả lời câu hỏi bằng tiếng Việt, chỉ dựa vào nguồn được cung cấp. Trả lời ngắn gọn, giữ điều kiện quan trọng và dẫn [n] cho nhận định có nguồn. Không suy ra hiệu lực hiện hành hoặc khẳng định vượt nguồn. Nếu nguồn thiếu, nói các đoạn được cung cấp chưa đủ căn cứ; không suy rộng thành toàn bộ corpus thiếu.'

def messages(r):
 sources='\n\n'.join(f"[{s['rank']}] {s['content']}" for s in r['sources']) or '(Không có nguồn)'
 return [{'role':'system','content':SYSTEM},{'role':'user','content':f"Câu hỏi: {r['query']}\nNguồn:\n{sources}"}]

def load_rows(split):return [json.loads(l) for l in (ROOT/'data'/f'{split}.jsonl').read_text().splitlines()]

def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['baseline','train','after']);p.add_argument('--model-path',required=True);a=p.parse_args()
 torch.manual_seed(42);random.seed(42)
 if not torch.cuda.is_available():raise RuntimeError('CUDA required for this configured experiment')
 out=ROOT/'runs/pilot-v1';out.mkdir(parents=True,exist_ok=True)
 config=dict(model_path=a.model_path,quantization='nf4-double',compute_dtype='bfloat16',seed=42,max_input_tokens=2048,max_new_tokens=192,context_budget_tokens=1400,do_sample=False,enable_thinking=False,system=SYSTEM,
 dataset_hashes={s:hashlib.sha256((ROOT/'data'/f'{s}.jsonl').read_bytes()).hexdigest() for s in ['train','dev','test','end-to-end']})
 if (out/'config.json').exists():assert json.loads((out/'config.json').read_text())==config
 else:(out/'config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2))
 tok=AutoTokenizer.from_pretrained(a.model_path);tok.pad_token=tok.eos_token
 quant=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
 model=AutoModelForCausalLM.from_pretrained(a.model_path,quantization_config=quant,device_map={'':0},dtype=torch.bfloat16)
 def prompt(r):return tok.apply_chat_template(messages(r),tokenize=False,add_generation_prompt=True,enable_thinking=False)
 if a.mode=='train':
  if not (out/'baseline.jsonl').exists():raise RuntimeError('Run baseline before training')
  expected=sum(len(load_rows(s)) for s in ['dev','test','end-to-end'])
  if len((out/'baseline.jsonl').read_text().splitlines()) != expected:raise RuntimeError('Baseline incomplete')
  model=prepare_model_for_kbit_training(model);model=get_peft_model(model,LoraConfig(r=8,lora_alpha=16,target_modules=['q_proj','v_proj'],lora_dropout=.05,task_type='CAUSAL_LM'))
  model.config.use_cache=False;model.train();opt=torch.optim.AdamW([x for x in model.parameters() if x.requires_grad],lr=1e-4)
  rows=load_rows('train');logs=[]
  # Fixed tiny teaching run, no tuning on test: 3 epochs, batch=1, accumulation=4.
  for epoch in range(3):
   random.shuffle(rows);opt.zero_grad()
   for i,r in enumerate(rows):
    prefix=tok(prompt(r),add_special_tokens=False)['input_ids'];target=tok(r['answer']+tok.eos_token,add_special_tokens=False)['input_ids']
    ids=prefix+target
    if len(ids)>2048:raise ValueError('Training example exceeds budget; no silent truncation')
    x=torch.tensor([ids],device='cuda');labels=x.clone();labels[:,:len(prefix)]=-100
    loss=model(input_ids=x,attention_mask=torch.ones_like(x),labels=labels).loss
    (loss/4).backward()
    if (i+1)%4==0 or i==len(rows)-1:
     torch.nn.utils.clip_grad_norm_(model.parameters(),1.0);opt.step();opt.zero_grad()
    logs.append(dict(epoch=epoch,case_id=r['case_id'],loss=float(loss.detach())))
   print('epoch',epoch+1,'mean loss',sum(x['loss'] for x in logs if x['epoch']==epoch)/len(rows),flush=True)
  model.save_pretrained(out/'adapter');(out/'training.json').write_text(json.dumps(logs,indent=2));return
 if a.mode=='after':model=PeftModel.from_pretrained(model,out/'adapter')
 model.eval()
 eos=model.generation_config.eos_token_id
 eos_ids=set(eos if isinstance(eos,list) else [eos])
 with (out/(a.mode+'.jsonl')).open('x') as f:
  for split in ['dev','test','end-to-end']:
   for original in load_rows(split):
    r = dict(original)
    omitted = []
    if split == 'end-to-end':
     kept=[]
     for source in r['sources']:
      candidate={**r,'sources':kept+[source]}
      if len(tok(prompt(candidate),add_special_tokens=False)['input_ids']) <= 1400:
       kept.append(source)
      else: omitted.append(source['chunk_id'])
     r['sources']=kept
    inputs=tok(prompt(r),return_tensors='pt',add_special_tokens=False).to('cuda');n=inputs.input_ids.shape[1]
    if n>2048:raise ValueError('Input exceeds budget; no silent truncation')
    start=time.perf_counter()
    with torch.inference_mode():y=model.generate(**inputs,max_new_tokens=192,do_sample=False,pad_token_id=tok.eos_token_id)
    text=tok.decode(y[0,n:],skip_special_tokens=True)
    result=dict(case_id=r['case_id'],split=split,sources=r['sources'],omitted_chunk_ids=omitted,answer=text,input_tokens=n,output_tokens=len(y[0])-n,seconds=time.perf_counter()-start,truncated=int(y[0,-1]) not in eos_ids)
    f.write(json.dumps(result,ensure_ascii=False)+'\n');f.flush();print(a.mode,r['case_id'],text[:90],flush=True)
if __name__=='__main__':main()
