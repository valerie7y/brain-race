import json, base64, urllib.parse, re
src='/workspace/brain-race/src/'
QB={}
for lvl,fn in (("8","q8.txt"),("12","q12.txt"),("adult","qadult.txt")):
    rows=[]
    for n,line in enumerate(open(src+fn,encoding='utf-8'),1):
        line=line.rstrip('\n')
        if not line.strip(): continue
        parts=line.split('|'); assert len(parts) in (6,7),(fn,n,len(parts))
        parts=[p.strip() for p in parts]; assert all(parts),(fn,n)
        if len(parts)==7:
            assert parts[6]=='E',(fn,n); parts[6]=1
        rows.append(parts)
    QB[lvl]=rows
svg=open(src+'icon.svg').read().strip()
ico180=base64.b64encode(open(src+'icon180.png','rb').read()).decode()
manifest={"name":"Brain Race","short_name":"Brain Race","start_url":"https://valerie7y.github.io/brain-race/","scope":"https://valerie7y.github.io/brain-race/","display":"standalone","background_color":"#FFF3D9","theme_color":"#7C3AED",
  "icons":[{"src":"data:image/png;base64,"+ico180,"sizes":"180x180","type":"image/png"},{"src":"data:image/svg+xml,"+urllib.parse.quote(svg),"sizes":"any","type":"image/svg+xml"}]}
t=open(src+'template.html',encoding='utf-8').read()
qjson=json.dumps(QB,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
t=t.replace('__QUESTIONS__',qjson)
t=t.replace('__ICON_SVG__',urllib.parse.quote(svg))
t=t.replace('__ICON180__',ico180)
t=t.replace('__MANIFEST__','data:application/manifest+json,'+urllib.parse.quote(json.dumps(manifest)))
t=t.replace('__ICON_INLINE__',svg.replace('id="g"','id="lg"').replace('url(#g)','url(#lg)'))
assert '__' not in re.sub(r'[a-z]__|__[a-z]','',t) or True
open('/workspace/brain-race/index.html','w',encoding='utf-8').write(t)
print({k:len(v) for k,v in QB.items()}, len(t)//1024,'KB')
