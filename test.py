import sys, json
from playwright.sync_api import sync_playwright
URL = sys.argv[1] if len(sys.argv)>1 else "http://localhost:8765/index.html"
SHOTS = "/workspace/brain-race/screens/"
errors=[]
def ok(c,msg):
    print(("PASS " if c else "FAIL ")+msg)
    if not c: errors.append(msg)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome")
    ctx=b.new_context(viewport={"width":390,"height":844}, device_scale_factor=3, is_mobile=True, has_touch=True)
    pg=ctx.new_page()
    jserr=[]
    pg.on("pageerror", lambda e: jserr.append(str(e)))
    pg.on("console", lambda m: jserr.append(m.text) if m.type=="error" else None)
    pg.on("dialog", lambda d: d.accept())
    pg.goto(URL); pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_selector("#qtext")
    st=lambda: pg.evaluate("BrainRace.state()")
    s=st()
    ok([x["name"] for x in s["players"]]==["Anthony","Liz","Eugene"], "default players Anthony/Liz/Eugene")
    ok([x["level"] for x in s["players"]]==["8","12","adult"], "default levels 8/12/adult")
    counts=pg.evaluate("Object.fromEntries(Object.entries(BrainRace.QB).map(([k,v])=>[k,v.length]))"); print("counts",counts)
    # turn 1: Anthony, level 8
    ok("Anthony" in pg.inner_text("#turnTitle") and s["cur"]["qid"].startswith("8:"), "turn 1 Anthony gets age-8 question")
    pg.click("#hintBtn"); pg.wait_for_timeout(300)
    ok(pg.locator(".hint").count()==1, "hint 1 shown")
    ok("+2" in pg.inner_text("#gotBtn"), "Got-it shows +2 after one hint")
    pg.screenshot(path=SHOTS+"1-question.png")
    pg.click("#gotBtn"); pg.wait_for_selector("#funFact")
    ok(st()["players"][0]["score"]==2, "Anthony +2 with 1 hint")
    pg.wait_for_timeout(600)
    pg.screenshot(path=SHOTS+"2-answer-funfact.png")
    pg.click("#nextBtn"); pg.wait_for_selector("#qtext")
    s=st(); ok("Liz" in pg.inner_text("#turnTitle") and s["cur"]["qid"].startswith("12:"), "turn 2 Liz gets age-12 question")
    pg.click("#gotBtn"); pg.wait_for_selector("#nextBtn")
    ok(st()["players"][1]["score"]==3, "Liz +3 with no hints")
    pg.click("#nextBtn"); pg.wait_for_selector("#qtext")
    s=st(); ok("Eugene" in pg.inner_text("#turnTitle") and s["cur"]["qid"].startswith("adult:"), "turn 3 Eugene gets expert question")
    pg.click("#hintBtn"); pg.click("#hintBtn"); pg.wait_for_timeout(200)
    ok(pg.is_disabled("#hintBtn") and "+1" in pg.inner_text("#gotBtn"), "max 2 hints, worth +1")
    # miss -> steal by Liz
    pg.click("#missBtn"); pg.wait_for_selector("[data-steal]")
    ok(pg.locator("[data-steal]").count()==2, "steal offered to the 2 other players")
    pg.click("[data-steal='p2']"); pg.wait_for_selector("#stealYesBtn")
    pg.click("#stealYesBtn"); pg.wait_for_selector("#resTitle")
    s=st(); ok(s["players"][1]["score"]==4 and s["players"][2]["score"]==0, "steal gives Liz +1 (4), Eugene 0")
    ok("stole" in pg.inner_text("#resTitle"), "steal result title")
    pg.click("#nextBtn"); pg.wait_for_selector("#qtext")
    ok("Anthony" in pg.inner_text("#turnTitle"), "turn wraps back to Anthony after Eugene")
    # miss with no steal
    pg.click("#missBtn"); pg.click("#noStealBtn"); pg.wait_for_selector("#funFact")
    ok(st()["players"][0]["score"]==2, "missed + no steal: no points")
    # manual adjust
    pg.click("[data-adj='p3'][data-d='1']"); pg.click("[data-adj='p3'][data-d='1']"); pg.click("[data-adj='p3'][data-d='-1']")
    ok(st()["players"][2]["score"]==1, "manual +/- adjusts Eugene to 1")
    # reload keeps score
    before=[x["score"] for x in st()["players"]]; used=st()["used"]
    pg.reload(); pg.wait_for_selector(".pcard")
    after=[x["score"] for x in st()["players"]]
    ok(before==after==[2,4,1], f"reload keeps scores {after}")
    ok(pg.inner_text("[data-testid='score-p2']")=="4", "scoreboard shows Liz 4 after reload")
    ok(st()["used"]==used, "used-question history persisted")
    # no repeats: ask many questions, check uniqueness within level
    pg.evaluate("""()=>{const S=BrainRace.state(); }""")
    seen=set(); dup=False
    for i in range(40):
        pg.click("#nextBtn") if pg.locator("#nextBtn").count() else None
        if pg.locator("#skipBtn").count(): pg.click("#skipBtn")
        q=st()["cur"]["qid"]
        if q in seen: dup=True
        seen.add(q)
    ok(not dup, "no repeated questions over 40 picks")
    # settings opens & level change
    pg.click("#btnSettings"); pg.wait_for_selector("#sheet .prow")
    ok(pg.locator("#sheet .prow").count()==3, "settings lists 3 players")
    pg.click("#closeSet")
    # winner: set target 15 and push Liz near target
    pg.evaluate("""()=>{const S=BrainRace.state(); S.target=15; }""")
    pg.click("#btnSettings"); pg.click("[data-target='15']"); pg.click("#closeSet")
    for _ in range(11): pg.click("[data-adj='p2'][data-d='1']")
    pg.wait_for_selector("#win:not([hidden])", timeout=3000)
    ok("Liz wins" in pg.inner_text("#winnerName"), "winner celebration for Liz at 15")
    pg.wait_for_timeout(1200)
    pg.screenshot(path=SHOTS+"3-winner.png")
    pg.click("#winNew"); pg.wait_for_timeout(300)
    ok([x["score"] for x in st()["players"]]==[0,0,0] and "Anthony" in pg.inner_text("#turnTitle"), "new game resets scores, Anthony first")
    ok(len(st()["used"]["8"])>0, "question history kept across new game")
    ok(not jserr, "no JS errors: "+json.dumps(jserr))
    b.close()
print("\nRESULT:", "ALL PASS" if not errors else f"{len(errors)} FAIL")
sys.exit(1 if errors else 0)
