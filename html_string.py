main_html = """<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ElectricalRAG - 基层配电知识助手</title>
    <!-- 引入科技感字体 -->
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
    <style>
        /* 全局样式 */
        :root {
            --primary-color: #1a73e8;
            --primary-hover: #1557b0;
            --background: linear-gradient(to bottom right, #0f0c29, #302b63, #24243e);
            --card-bg: rgba(255, 255, 255, 0.05);
            --text-primary: #ffffff;
            --text-secondary: #cccccc;
            --shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        body {
            font-family: 'Orbitron', 'Segoe UI', sans-serif; /* 科技字体 */
            background: var(--background);
            color: var(--text-primary);
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        header {
            background: linear-gradient(135deg, var(--primary-color), #42a5f5);
            color: white;
            width: 100%;
            padding: 2em 1em;
            text-align: center;
            box-shadow: var(--shadow);
            position: relative;
            overflow: hidden;
        }

        /* 添加 header 装饰线条（引用[[5]]倾斜效果） */
        header::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: -50%;
            width: 200%;
            height: 40px;
            background: rgba(255,255,255,0.1);
            transform: rotate(-3deg);
            transform-origin: left bottom;
        }

        main {
            margin: 2em auto;
            background-color: var(--card-bg);
            border-radius: 12px;
            box-shadow: var(--shadow);
            width: 90%;
            max-width: 800px;
            padding: 2.5em;
            position: relative;
            backdrop-filter: blur(8px); /* 毛玻璃效果 */
        }

        h1 {
            margin: 0;
            font-size: 1.8em;
            font-weight: 600;
            letter-spacing: 1px;
        }

        p {
            color: var(--text-secondary);
            font-size: 1.1em;
            line-height: 1.6;
            margin: 1.2em 0;
        }

        a {
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 500;
            border-bottom: 1px dashed var(--primary-color);
            transition: all 0.3s ease;
        }

        a:hover {
            color: var(--primary-hover);
            border-bottom: 1px solid var(--primary-hover);
        }

        ul {
            list-style-type: none;
            padding: 0;
            margin-top: 2.5em;
        }

        li {
            margin: 0.8em 0;
        }

        /* 卡片升级样式 */
        .nav-card {
            background: var(--card-bg);
            backdrop-filter: blur(8px); /* 半透明 */
            padding: 1.2em 1.5em;
            border-radius: 12px;
            transition: all 0.3s ease;
            box-shadow: var(--shadow);
            transform: translateY(0);
            position: relative;
            overflow: hidden;
        }

        /* 卡片悬停动画 */
        .nav-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
            background: linear-gradient(135deg, var(--primary-color), #42a5f5); /* 渐变动效 */
        }

        /* 按钮光效（引用[[3]]动态效果） */
        .nav-link {
            color: white;
            text-decoration: none;
            display: flex;
            align-items: center;
            font-size: 1.1em;
            font-weight: 500;
            transition: opacity 0.3s;
            position: relative;
            padding: 8px 12px;
            border-radius: 8px;
        }

        .nav-link::before {
            content: '';
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: linear-gradient(90deg, var(--primary-color), #42a5f5);
            border-radius: 8px;
            opacity: 0.2;
            transition: opacity 0.3s;
            z-index: -1;
        }

        .nav-link:hover::before {
            opacity: 1;
        }

        /* 六边形步骤编号（引用[[3]]几何元素） */
        .step-number {
            clip-path: polygon(50% 0%, 80% 25%, 80% 75%, 50% 100%, 20% 75%, 20% 25%);
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--primary-color);
            color: white;
            font-weight: bold;
            margin-right: 0.6em;
        }

        .features {
            margin-top: 2.5em;
            padding-top: 2em;
            border-top: 1px solid rgba(255,255,255,0.1);
        }

        .features h2 {
            font-size: 1.4em;
            color: var(--primary-color);
            margin-bottom: 1em;
            border-left: 3px solid var(--primary-color);
            padding-left: 0.5em;
        }

        .feature-list {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.2em;
            list-style: none;
            padding-left: 0;
        }

        .feature-item {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(6px);
            padding: 1em;
            border-radius: 12px;
            display: flex;
            align-items: center;
            transition: transform 0.3s;
        }

        .feature-item:hover {
            transform: translateX(5px);
        }

        .feature-icon {
            color: var(--primary-color);
            margin-right: 0.5em;
            font-size: 18px;
        }

        /* 响应式优化 */
        @media (max-width: 600px) {
            main {
                padding: 1.5em 1em;
            }
            
            .feature-list {
                grid-template-columns: 1fr;
            }

            .nav-link {
                font-size: 1em;
                padding: 12px 16px;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>ElectricalRAG - 基层配电知识助手</h1>
    </header>
    
    <main>
        <p>如果您需要基于上传的文档与模型直接对话，请访问 <a href="/chat">RAG问答</a> 并在输入框上传文件即可开始对话。（本次上传的数据将在页面刷新后清除，如需持久使用请创建知识库）</p>
        
        <p>如需创建或更新知识库，请按照 <a href="/upload_data">上传数据</a>、<a href="/create_knowledge_base">创建知识库</a> 的流程操作，在 <a href="/chat">RAG问答</a> 中选择对应的知识库即可使用。</p>
        
        <p>您也可以直接访问 <a href="/chat">RAG问答</a> 页面，从已有知识库中选择进行问答。</p>
        
        <ul>
            <li>
                <div class="nav-card">
                    <a class="nav-link" href="/upload_data">
                        <span class="step-number">1</span>
                        <span class="material-icons">file_upload</span>
                        <span>1. 上传数据</span>
                    </a>
                </div>
            </li>
            <li>
                <div class="nav-card">
                    <a class="nav-link" href="/create_knowledge_base">
                        <span class="step-number">2</span>
                        <span class="material-icons">library_add</span>
                        <span>2. 创建知识库</span>
                    </a>
                </div>
            </li>
            <li>
                <div class="nav-card">
                    <a class="nav-link" href="/chat">
                        <span class="step-number">3</span>
                        <span class="material-icons">chat</span>
                        <span>3. RAG问答</span>
                    </a>
                </div>
            </li>
        </ul>

        <div class="features">
            <h2>核心功能</h2>
            <ul class="feature-list">
                <li class="feature-item">
                    <span class="material-icons feature-icon">cloud_upload</span>
                    <span>支持多种文档格式上传</span>
                </li>
                <li class="feature-item">
                    <span class="material-icons feature-icon">storage</span>
                    <span>知识库持久化存储</span>
                </li>
                <li class="feature-item">
                    <span class="material-icons feature-icon">auto_stories</span>
                    <span>智能文档解析</span>
                </li>
                <li class="feature-item">
                    <span class="material-icons feature-icon">question_answer</span>
                    <span>自然语言交互问答</span>
                </li>
            </ul>
        </div>
    </main>
</body>
</html>"""

plain_html = """<!DOCTYPE html>
<html lang="zh">
    <head>
        <title>RAG问答</title>
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
        <style>
        .links-container {
            display: flex;
            justify-content: center; /* 在容器中居中分布子元素 */
            list-style-type: none; /* 去掉ul默认的列表样式 */
            padding: 0; /* 去掉ul默认的内边距 */
            margin: 0; /* 去掉ul默认的外边距 */
        }
        .links-container li {
            margin: 0 5px; /* 每个li元素的左右留出一些空间 */
            padding: 10px 15px; /* 添加内边距 */
            border: 1px solid #ccc; /* 添加边框 */
            border-radius: 5px; /* 添加圆角 */
            background-color: #f9f9f9; /* 背景颜色 */
            transition: background-color 0.3s; /* 背景颜色变化的过渡效果 */
            display: flex; /* 使用flex布局 */
            align-items: center; /* 垂直居中对齐 */
            height: 50px; /* 设置固定高度，确保一致 */
        }
        .links-container li:hover {
            background-color: #e0e0e0; /* 悬停时的背景颜色 */
        }
        .links-container a {
            text-decoration: none !important; /* 去掉链接的下划线 */
            color: #333; /* 链接颜色 */
            font-family: Arial, sans-serif; /* 字体 */
            font-size: 14px; /* 字体大小 */
            display: flex; /* 使用flex布局 */
            align-items: center; /* 垂直居中对齐 */
            height: 100%; /* 确保链接高度与父元素一致 */
        }
        .material-icons {
            font-size: 20px; /* 图标大小 */
            margin-right: 8px; /* 图标和文字间的间距 */
            text-decoration: none; /* 确保图标没有下划线 */
        }

        /* 深色模式样式 */
        @media (prefers-color-scheme: dark) {
            .links-container li {
                background-color: #333; /* 深色模式下的背景颜色 */
                border-color: #555; /* 深色模式下的边框颜色 */
            }
            .links-container li:hover {
                background-color: #555; /* 深色模式下悬停时的背景颜色 */
            }
            .links-container a {
                color: #f9f9f9; /* 深色模式下的文字颜色 */
            }
        }
        </style>
    </head>
    <body>
        <ul class="links-container">
            <li><a href="/"><span class="material-icons">home</span> 主页</a></li>
            <li><a href="/upload_data"><span class="material-icons">cloud_upload</span> 上传数据</a></li>
            <li><a href="/create_knowledge_base"><span class="material-icons">library_add</span> 创建知识库</a></li>
            <li><a href="/chat"><span class="material-icons">question_answer</span> RAG问答</a></li>
        </ul>
    </body>
</html>"""
