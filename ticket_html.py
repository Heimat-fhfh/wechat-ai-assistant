from datetime import datetime
from define import GENERATED_HTML_DIR
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_file_exists(directory, filename):
    """
    检查指定目录下是否存在指定文件
    
    Args:
        directory (str): 目录路径
        filename (str): 文件名
    
    Returns:
        bool: 文件存在返回True，否则返回False
    """
    file_path = os.path.join(directory, filename)
    return os.path.exists(file_path)


def generate_ticket_html(data, filename='mobile_tickets.html', title='火车票信息查询结果'):
    """
    生成移动端友好的火车票信息HTML表格
    
    参数:
    data -- 处理后的字典数组数据
    filename -- 输出HTML文件名
    title -- 页面标题
    """
    if data == "station_code_Error":
        return data
    elif data == "no_ticket":
        return "no_ticket"

    if check_file_exists(GENERATED_HTML_DIR,filename) == True:
        logger.info("文件已经存在")
        return filename
    
    if not data:
        logger.error("generate_ticket_html未接收到数据")
        return ''
    
    # 创建HTML页面结构
    html_template = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            :root {{
                --primary-color: #1a73e8;
                --secondary-color: #4285f4;
                --success-color: #0f9d58;
                --danger-color: #db4437;
                --warning-color: #f4b400;
                --light-gray: #f5f7fa;
                --border-color: #e0e0e0;
                --text-color: #333;
                --text-light: #5f6368;
            }}
            
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}
            
            body {{
                font-family: 'Microsoft YaHei', Arial, sans-serif;
                margin: 0;
                padding: 10px;
                background-color: var(--light-gray);
                color: var(--text-color);
                font-size: 14px;
                line-height: 1.4;
            }}
            
            .container {{
                max-width: 100%;
                margin: 0 auto;
            }}
            
            .header {{
                text-align: center;
                padding: 15px 0;
                margin-bottom: 10px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }}
            
            .header h1 {{
                color: var(--primary-color);
                margin: 0;
                font-size: 18px;
            }}
            
            .header .subtitle {{
                color: var(--text-light);
                margin-top: 5px;
                font-size: 12px;
            }}
            
            .filters {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-bottom: 12px;
                background: white;
                padding: 10px;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }}
            
            .filter-btn {{
                padding: 6px 12px;
                background: white;
                border: 1px solid var(--border-color);
                border-radius: 16px;
                font-size: 12px;
                cursor: pointer;
                transition: all 0.2s;
            }}
            
            .filter-btn.active {{
                background: var(--primary-color);
                color: white;
                border-color: var(--primary-color);
            }}
            
            .ticket-list {{
                display: flex;
                flex-direction: column;
                gap: 8px;
            }}
            
            .ticket-card {{
                background: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            
            .ticket-card:active {{
                transform: scale(0.98);
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            
            .ticket-header {{
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                padding: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .train-number {{
                font-size: 16px;
                font-weight: bold;
            }}
            
            .train-tags {{
                display: flex;
                gap: 5px;
            }}
            
            .tag {{
                background: rgba(255,255,255,0.2);
                padding: 3px 6px;
                border-radius: 3px;
                font-size: 10px;
            }}
            
            .ticket-body {{
                padding: 12px;
            }}
            
            .route-info {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }}
            
            .station {{
                display: flex;
                flex-direction: column;
                align-items: center;
                flex: 1;
            }}
            
            .station-name {{
                font-weight: bold;
                font-size: 14px;
                margin-bottom: 3px;
            }}
            
            .station-time {{
                color: var(--text-light);
                font-size: 12px;
            }}
            
            .duration {{
                text-align: center;
                color: var(--text-light);
                font-size: 11px;
                margin: 0 5px;
            }}
            
            .arrow {{
                font-size: 16px;
                color: var(--text-light);
                margin: 0 5px;
            }}
            
            .prices-container {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 8px;
                margin-top: 10px;
            }}
            
            .price-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 6px 8px;
                background: #f9f9f9;
                border-radius: 4px;
                font-size: 12px;
            }}
            
            .seat-type {{
                font-weight: bold;
            }}
            
            .available {{
                color: var(--success-color);
                font-weight: bold;
            }}
            
            .unavailable {{
                color: var(--danger-color);
            }}
            
            .limited {{
                color: var(--warning-color);
                font-weight: bold;
            }}
            
            .footer {{
                text-align: center;
                margin-top: 20px;
                padding: 15px;
                color: var(--text-light);
                font-size: 12px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }}
            
            /* 桌面端适配 */
            @media (min-width: 768px) {{
                body {{
                    padding: 20px;
                }}
                
                .container {{
                    max-width: 800px;
                }}
                
                .prices-container {{
                    grid-template-columns: repeat(4, 1fr);
                }}
                
                .header h1 {{
                    font-size: 24px;
                }}
            }}
            
            /* 暗色模式支持 */
            @media (prefers-color-scheme: dark) {{
                body {{
                    background-color: #121212;
                    color: #e0e0e0;
                }}
                
                .header, .filters, .ticket-card, .footer {{
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                }}
                
                .filter-btn {{
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                    border-color: #444;
                }}
                
                .price-item {{
                    background-color: #2d2d2d;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{title}</h1>
                <div class="subtitle">查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 共找到 {len(data)} 个车次</div>
            </div>
            
            <div class="filters">
                <button class="filter-btn active" data-filter="all">全部</button>
                <button class="filter-btn" data-filter="available">有票</button>
                <button class="filter-btn" data-filter="highspeed">高铁/动车</button>
                <button class="filter-btn" data-filter="normal">普通列车</button>
            </div>
            
            <div class="ticket-list">
                {{ticket_cards}}
            </div>
            
            <div class="footer">
                数据仅供参考，请以12306官方信息为准
            </div>
        </div>
        
        <script>
            // 简单的筛选功能
            document.querySelectorAll('.filter-btn').forEach(btn => {{
                btn.addEventListener('click', function() {{
                    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    
                    const filter = this.getAttribute('data-filter');
                    const tickets = document.querySelectorAll('.ticket-card');
                    
                    tickets.forEach(ticket => {{
                        if (filter === 'all') {{
                            ticket.style.display = 'block';
                        }} else if (filter === 'available') {{
                            if (ticket.querySelector('.available')) {{
                                ticket.style.display = 'block';
                            }} else {{
                                ticket.style.display = 'none';
                            }}
                        }} else if (filter === 'highspeed') {{
                            const trainNum = ticket.querySelector('.train-number').textContent;
                            if (trainNum.startsWith('G') || trainNum.startsWith('D') || trainNum.startsWith('C')) {{
                                ticket.style.display = 'block';
                            }} else {{
                                ticket.style.display = 'none';
                            }}
                        }} else if (filter === 'normal') {{
                            const trainNum = ticket.querySelector('.train-number').textContent;
                            if (trainNum.startsWith('G') || trainNum.startsWith('D') || trainNum.startsWith('C')) {{
                                ticket.style.display = 'none';
                            }} else {{
                                ticket.style.display = 'block';
                            }}
                        }}
                    }});
                }});
            }});
        </script>
    </body>
    </html>
    """
    
    # 生成每个车次的HTML卡片
    ticket_cards_html = ""
    for ticket in data:
        # 解析票价信息
        price_items = ""
        if '票价信息' in ticket and ticket['票价信息']:
            for seat_type, price_info in ticket['票价信息'].items():
                # 判断票务状态
                if '无票' in price_info:
                    status_class = "unavailable"
                    status_text = "无票"
                    price = price_info.replace('无票', '')
                elif '有票' in price_info:
                    status_class = "available"
                    status_text = "有票"
                    price = price_info.replace('有票', '')
                elif '剩余' in price_info:
                    status_class = "limited"
                    # 提取剩余票数
                    import re
                    match = re.search(r'剩余(\d+)张票', price_info)
                    if match:
                        status_text = f"{match.group(1)}张"
                        price = price_info.replace(f'剩余{match.group(1)}张票', '')
                    else:
                        status_text = "有票"
                        price = price_info
                else:
                    status_class = "unavailable"
                    status_text = "无票"
                    price = price_info
                
                price_items += f"""
                <div class="price-item">
                    <span class="seat-type">{seat_type}</span>
                    <span class="{status_class}">{status_text} {price}</span>
                </div>
                """
        
        # 创建单个车次卡片（紧凑布局）
        ticket_card = f"""
        <div class="ticket-card">
            <div class="ticket-header">
                <div class="train-number">{ticket.get('车次', 'N/A')}</div>
                <div class="train-tags">
                    <span class="tag">{ticket.get('特色标签', '')}</span>
                </div>
            </div>
            <div class="ticket-body">
                <div class="route-info">
                    <div class="station">
                        <div class="station-name">{ticket.get('出发站', 'N/A').split('(')[0]}</div>
                        <div class="station-time">{ticket.get('出发时间', 'N/A')}</div>
                    </div>
                    <div class="duration">
                        <div class="arrow">→</div>
                        <div>{ticket.get('历时', 'N/A')}</div>
                    </div>
                    <div class="station">
                        <div class="station-name">{ticket.get('到达站', 'N/A').split('(')[0]}</div>
                        <div class="station-time">{ticket.get('到达时间', 'N/A')}</div>
                    </div>
                </div>
                
                <div class="prices-container">
                    {price_items}
                </div>
            </div>
        </div>
        """
        
        ticket_cards_html += ticket_card
    
    # 将卡片HTML插入到模板中
    final_html = html_template.replace("{ticket_cards}", ticket_cards_html)
    
    # 保存HTML文件
    with open(GENERATED_HTML_DIR+filename, 'w', encoding='utf-8') as f:
        f.write(final_html)
    return filename
    


if __name__ == "__main__":
    # 示例数据
    sample_data = [
        {
            '车次': 'K466', 
            '实际车次train_no': '5e0000K4660B', 
            '出发站': '芜湖(telecode:WHH)', 
            '到达站': '合肥(telecode: HFH)', 
            '出发时间': '20:06', 
            '到达时间': '21:38', 
            '历时': '01:32', 
            '票价': '[硬座: 无票23.5元,软卧: 无票104.5元,硬卧: 无票69.5元,无座: 无票23.5元,]', 
            '特色标签': '支持选铺', 
            '票价信息': {
                '硬座': '无票23.5元', 
                '软卧': '无票104.5元', 
                '硬卧': '无票69.5元', 
                '无座': '无票23.5元'
            }
        },
        {
            '车次': 'K2276', 
            '实际车次train_no': '56000K227650', 
            '出发站': '芜湖(telecode:WHH)', 
            '到达站': '合肥(telecode: HFH)', 
            '出发时间': '19:01', 
            '到达时间': '20:54', 
            '历时': '01:53', 
            '票价': '[硬卧: 剩余16张票69.5元,软卧: 剩余1张票104.5元,硬座: 有票23.5元,无座: 有票23.5元,]', 
            '特色标签': '支持选铺', 
            '票价信息': {
                '硬卧': '剩余16张票69.5元', 
                '软卧': '剩余1张票104.5元', 
                '硬座': '有票23.5元', 
                '无座': '有票23.5元'
            }
        },
        {
            '车次': 'G1234', 
            '实际车次train_no': '5g000G12340A', 
            '出发站': '北京南(telecode:BJP)', 
            '到达站': '上海虹桥(telecode: AOH)', 
            '出发时间': '09:00', 
            '到达时间': '13:45', 
            '历时': '04:45', 
            '票价': '[二等座: 有票553元,一等座: 剩余12张票933元,商务座: 剩余2张票1748元,]', 
            '特色标签': '复兴号', 
            '票价信息': {
                '二等座': '有票553元', 
                '一等座': '剩余12张票933元', 
                '商务座': '剩余2张票1748元'
            }
        },
        {
            '车次': 'D735', 
            '实际车次train_no': '5d000D7350C', 
            '出发站': '南京南(telecode:NKH)', 
            '到达站': '杭州东(telecode: HGH)', 
            '出发时间': '14:20', 
            '到达时间': '16:05', 
            '历时': '01:45', 
            '票价': '[二等座: 无票117元,一等座: 无票188元,]', 
            '特色标签': '动车', 
            '票价信息': {
                '二等座': '无票117元', 
                '一等座': '无票188元'
            }
        }
    ]

    # 生成HTML文件
    generate_ticket_html(sample_data, 'mobile_train_tickets.html', '火车票查询结果')