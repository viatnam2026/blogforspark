import os
import datetime
import requests
import feedparser

def get_bitcoin_price():
    """获取比特币实时行情数据（通过公开行情接口）"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        btc_data = data.get("bitcoin", {})
        price = btc_data.get("usd", "N/A")
        change_24h = btc_data.get("usd_24h_change", 0.0)
        return {
            "price": f"${price:,.2f}" if isinstance(price, (int, float)) else str(price),
            "change": f"{change_24h:+.2f}%" if isinstance(change_24h, (int, float)) else "0.00%"
        }
    except Exception as e:
        print(f"获取比特币价格失败: {e}")
        return {"price": "获取失败", "change": "0.00%"}

def fetch_rss_news():
    """抓取主流新闻 RSS 订阅源"""
    feeds = {
        "地缘政治与国际要闻": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "科技与人工智能": "https://techcrunch.com/feed/",
        "加密金融": "https://www.coindesk.com/arc/outboundfeeds/rss/"
    }
    
    news_data = {}
    for category, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            items = []
            for entry in feed.entries[:4]:  # 取前4条精选
                items.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", "#"),
                    "summary": entry.get("summary", "")[:180] + "..." if entry.get("summary") else ""
                })
            news_data[category] = items
        except Exception as e:
            print(f"抓取 {category} 失败: {e}")
            news_data[category] = []
    return news_data

def build_html(btc_info, news_dict):
    """生成单页静态 HTML 简报"""
    today_str = datetime.datetime.now(datetime.timezone.utc).strftime('%Y年%m月%d日 (UTC)')
    
    categories_html = ""
    for category, articles in news_dict.items():
        articles_html = ""
        for item in articles:
            articles_html += f"""
            <div class="article-card">
                <h3><a href="{item['link']}" target="_blank" rel="noopener noreferrer">{item['title']}</a></h3>
                <p>{item['summary']}</p>
            </div>
            """
        categories_html += f"""
        <section class="section">
            <h2>{category}</h2>
            <div class="article-list">
                {articles_html}
            </div>
        </section>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日观察与市场简报 - {today_str}</title>
    <style>
        :root {{
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #1e293b;
            --text-sub: #64748b;
            --accent: #2563eb;
            --border: #e2e8f0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 2rem 1rem;
            line-height: 1.6;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        header {{
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 1rem;
        }}
        h1 {{ margin: 0 0 0.5rem 0; font-size: 1.8rem; }}
        .date {{ color: var(--text-sub); font-size: 0.95rem; }}
        
        .market-banner {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.2rem;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .price-badge {{ font-size: 1.3rem; font-weight: bold; }}
        .badge-up {{ color: #16a34a; }}
        .badge-down {{ color: #dc2626; }}

        .section {{ margin-bottom: 2.5rem; }}
        .section h2 {{
            font-size: 1.3rem;
            border-left: 4px solid var(--accent);
            padding-left: 0.6rem;
            margin-bottom: 1rem;
        }}
        .article-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 1rem 1.2rem;
            margin-bottom: 0.8rem;
        }}
        .article-card h3 {{ margin: 0 0 0.4rem 0; font-size: 1.05rem; }}
        .article-card a {{ color: var(--accent); text-decoration: none; }}
        .article-card a:hover {{ text-decoration: underline; }}
        .article-card p {{ margin: 0; color: var(--text-sub); font-size: 0.9rem; }}
        
        footer {{
            text-align: center;
            color: var(--text-sub);
            font-size: 0.85rem;
            margin-top: 3rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>每日重点观察与市场简报</h1>
            <div class="date">更新时间：{today_str}</div>
        </header>

        <div class="market-banner">
            <div>
                <strong>Bitcoin (BTC / USD)</strong>
                <div style="font-size: 0.85rem; color: var(--text-sub);">24 小时实时行情</div>
            </div>
            <div class="price-badge">
                {btc_info['price']}
                <span class="{'badge-up' if '+' in btc_info['change'] else 'badge-down'}" style="font-size: 0.95rem;">({btc_info['change']})</span>
            </div>
        </div>

        {categories_html}

        <footer>
            由 GitHub Actions 自动化构建与发布 · 部署于 GitHub Pages
        </footer>
    </div>
</body>
</html>
"""
    os.makedirs("public", exist_ok=True)
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("静态文件 public/index.html 生成完毕。")

if __name__ == "__main__":
    btc = get_bitcoin_price()
    news = fetch_rss_news()
    build_html(btc, news)
