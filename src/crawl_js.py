from playwright.sync_api import sync_playwright

def extract_with_js(url, selectores: dict, max_scrolls=8, wait_ms=900):
    data = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.set_extra_http_headers({"User-Agent":"AppanameBot/1.0"})
        page.goto(url, wait_until="networkidle", timeout=45000)

        last_height = 0
        for _ in range(max_scrolls):
            page.wait_for_timeout(wait_ms)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(wait_ms)
            new_h = page.evaluate("document.body.scrollHeight")
            if new_h == last_height:
                break
            last_height = new_h

        for selector in ["text=ver más", "text=ver mas", "text=cargar más", "text=cargar mas"]:
            try:
                while page.query_selector(selector):
                    page.click(selector)
                    page.wait_for_timeout(wait_ms)
            except:
                pass

        sel_title = selectores.get("comerciante") or selectores.get("beneficio") or "h2, h3, [class*=beneficio]"
        sel_disc  = selectores.get("descuento") or ".badge, .percent, [class*=descuento]"
        sel_terms = selectores.get("términos") or selectores.get("terminos") or ".tyc, .bases, .modal"

        titles = [el.inner_text().strip() for el in page.query_selector_all(sel_title)]
        discs  = [el.inner_text().strip() for el in page.query_selector_all(sel_disc)]
        terms  = [el.inner_text().strip() for el in page.query_selector_all(sel_terms)][:10]

        for i, t in enumerate(titles):
            data.append({
                "comerciante_o_beneficio": t,
                "descuento": discs[i] if i < len(discs) else "",
                "terminos_hint": "; ".join(terms[:2]) if terms else ""
            })

        browser.close()
    return data
