import time
from assemble_languages import assemble
for _ in range(720):
 done=[]
 for lang in ['pt','es','en']:
  result=assemble(lang)
  if result:done.append(lang)
 if len(done)==3:break
 time.sleep(60)
