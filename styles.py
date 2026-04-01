def get_custom_css():
    return """
    <style>
    /* 玻璃拟态卡片 */
    .stMetric {
        background: rgba(23, 28, 36, 0.8);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .alpha-card {
        background: rgba(23, 28, 36, 0.8);
        padding: 20px;
        border-left: 5px solid #00FFBD;
        border-radius: 8px;
        margin-bottom: 20px;
        transition: transform 0.3s;
    }
    
    .alpha-card:hover {
        transform: translateY(-5px);
        background: rgba(30, 38, 50, 0.9);
    }

    .sentiment-bullish { border-left-color: #00FFBD; }
    .sentiment-bearish { border-left-color: #FF3B6A; }
    .sentiment-neutral { border-left-color: #888888; }
    
    .ticker-tag {
        background: #1e3a8a;
        color: #60a5fa;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-right: 5px;
    }
    </style>
    """
