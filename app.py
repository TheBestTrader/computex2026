"""
COMPUTEX 2026 - 展會戰情儀表板
用法: streamlit run app.py
"""
import streamlit as st
import json
from datetime import datetime

st.set_page_config(
    page_title="COMPUTEX 2026 展會戰情",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
.vendor-card {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    margin-bottom: 18px;
    overflow: hidden;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    background: white;
}
.card-header { color: white; padding: 12px 16px; }
.card-header .company-name { font-size: 16px; font-weight: bold; line-height: 1.3; }
.card-header .brand-booth { font-size: 12px; opacity: 0.85; margin-top: 3px; }
.card-header .stars { font-size: 16px; float: right; color: #FFD700; margin-top: -2px; }
.card-body { padding: 12px 16px 4px; }
.badge {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: bold;
    margin-right: 5px;
    margin-bottom: 8px;
}
.killer-q {
    background: #FFF8E1;
    border-left: 4px solid #FF8F00;
    padding: 10px 13px;
    border-radius: 0 6px 6px 0;
    margin: 8px 0 10px;
}
.killer-q .kq-label { font-size: 11px; font-weight: bold; color: #E65100; margin-bottom: 4px; }
.killer-q .kq-text  { font-size: 13px; color: #4E342E; line-height: 1.55; }
hr.card-sep { border: none; border-top: 1px solid #f0f0f0; margin: 0; }
</style>
""", unsafe_allow_html=True)

# ── 廠商資料 ─────────────────────────────────────────────────────────────────
THEME_COLORS = {
    "主題一": "#1a73e8",
    "主題二": "#7c4dff",
    "主題三": "#0d9488",
    "補充":   "#f59e0b",
}
OSAT_COLORS = {
    "極高": "#dc2626",
    "高":   "#ea580c",
    "中等": "#ca8a04",
    "偏低": "#6b7280",
}

VENDORS = [
    # ── 主題一：製造業 AI ＋ 可解釋 AI (PINN) ──────────────────────────────
    dict(id="solomon", name="所羅門股份有限公司", brand="SOLOMON", booth="A0811a",
         zone="世貿一館 AI機器人區", priority=3, theme="主題一",
         core="機器視覺AI（半導體/PCB/SMT檢測）",
         tags=["AI","SmartManufacturing"],
         tech="3D 機器視覺 (AccuPick) + 深度學習。近期導入生成式 AI 模擬仿真稀少瑕疵樣本，解決訓練資料不足問題。",
         pinn="【混合約束，非純 PINN】手臂防撞與路徑規劃結合幾何學認知與傳統 AI，具備物理規則約束。瑕疵檢測偏向傳統深度學習分類，可解釋性中等。",
         osat="極高", osat_detail="明確具備半導體、EMS 封裝等產線落地經驗，客戶涵蓋各大國際廠。",
         kq="你們的瑕疵生成模型，產線工程師有辦法回推它誤判的原因嗎？參數權重可以解釋嗎？"),

    dict(id="gmm", name="均華精密工業股份有限公司", brand="GMM / GPM / G2C / 志聖", booth="A0704",
         zone="世貿一館 AI機器人區", priority=3, theme="主題一",
         core="IC 封裝設備（直接 OSAT 相關）",
         tags=["IC設計封裝","自動化整廠"],
         tech="核心為半導體晶片挑揀、封裝設備與自動化硬體整合，是 OSAT 設備主力供應商。",
         pinn="【需依賴外部 AI 軟體】本身為設備商，需確認機台是否能提供高頻率 OT 數據，以利訓練可解釋 AI 模型。",
         osat="極高", osat_detail="本身就是 OSAT 設備供應商主力，深諳封裝廠痛點。",
         kq="如果我們自己開發了 PINN 演算法，你們的機台控制底層能開放 API 讓我們直接下控嗎？"),

    dict(id="foresight", name="先知科技股份有限公司", brand="FS-Technology", booth="R0824",
         zone="南港二館 AI運算系統區", priority=3, theme="主題一",
         core="影像辨識服務 / AI Platform / DigitalTwin",
         tags=["AI","AI Platform","AI Service","DigitalTwin"],
         tech="OT/IT/AI 跨域數據匯流平台。主打模組化即選即用的 AI 系統平台，支援數位孿生。",
         pinn="【數據決策解釋】強調跨域數據驅動決策，自動化建模工具在決策樹與特徵重要性上具備商業可解釋性。",
         osat="中等", osat_detail="廣泛應用於傳統製造業，OSAT 直接案例需現場確認。",
         kq="在半導體封裝的高頻微秒級數據中，你們的平台吞吐量撐得住嗎？有 OSAT 真實案例嗎？"),

    dict(id="ironyun", name="鐵雲科技股份有限公司", brand="IRONYUN / VAIDIO", booth="R0634",
         zone="南港二館 AI運算系統區", priority=3, theme="主題二",
         core="Vaidio AI 視訊分析平台 / Agentic AI / VLM",
         tags=["AI","AI Platform","ComputerVision","LLM"],
         tech="Vaidio AI 視訊分析平台；全面整合 NVIDIA NIM 微服務與視覺語言模型（VLM），支援自然語言描述異常事件與場景摘要。",
         pinn="【視覺代理與自然語言微調】導入 Agentic AI 概念，能自主分析攝影機場景並推薦最佳配置參數；具備 CLIP 引擎，可透過自然語言進行微調與事件摘要，縮小認知誤差。",
         osat="極高", osat_detail="平台支援萬級攝影機規模，廣泛應用於大型場館、機場與廠區的自動化安防警報，具備明確的大規模落地實績。",
         kq="你們的視覺 AI 代理在自動配置攝影機參數時，若發生誤判，系統是否有『人類在迴路（Human-in-the-loop）』的覆寫與自動修正機制？"),

    dict(id="vaisense", name="普維科技有限公司", brand="VAISense", booth="R0932a",
         zone="南港二館 AI運算系統區", priority=2, theme="主題一",
         core="AI Platform（SmartManufacturing 方向）",
         tags=["AI","AI Platform","EdgeAI","SmartManufacturing"],
         tech="基於邊緣運算的影像分析平台，主打嵌入式晶片（高通或邊緣端 NPU）的推理優化。",
         pinn="【黑盒子邊緣化，非 PINN】核心在把 vision model 塞進工廠邊緣硬體，決策邏輯仍是純深度學習分類。",
         osat="中等", osat_detail="多用於廠務、產線人員動作合規性檢測，高階機台內檢測較少。",
         kq="在 OSAT 廠高精密、微秒級的產線動態中，你們的 Edge AI 算力延遲（Latency）表現如何？如何防範誤判？"),

    dict(id="otobrite", name="歐特明電子股份有限公司", brand="oToBrite", booth="A1225a",
         zone="世貿一館 AI機器人區", priority=2, theme="主題一",
         core="機器人 + 視覺AI + AMR",
         tags=["AI","AMR","AutonomousVehicles","Robotics"],
         tech="車載等級機器視覺與超音波感知融合，延伸至工業 AMR 導航與避障。",
         pinn="【幾何運動約束】AI 結合 SLAM 與空間幾何演算法，具備物理空間規則限制，但非製程上的 PINN。",
         osat="中等", osat_detail="主要落地在封裝廠內部物料搬運、AMR 自動巡檢，非機台內晶片檢測。",
         kq="你們的 AMR 視覺導航，在半導體無塵室（黃光區或複雜反光環境）的定位精準度表現如何？"),

    dict(id="microip", name="擷發科技股份有限公司", brand="MICROIP", booth="A1215a",
         zone="世貿一館 AI機器人區", priority=2, theme="主題一",
         core="影像辨識服務 / IC 設計服務",
         tags=["AI","SmartManufacturing","IC Design"],
         tech="影像辨識服務與 IC 設計服務雙軌並行，擅長底層晶片架構優化。",
         pinn="【特徵值分析】偏向傳統 CNN 影像處理優化，在 IC 測試階段有統計學上的可解釋性。",
         osat="高", osat_detail="本身具備 IC 設計背景，對半導體測試、晶圓外觀瑕疵檢測（AOI）的需求痛點非常熟悉。",
         kq="你們的影像辨識演算法在面對 OSAT 廠未知的全新瑕疵類型時，如何避免模型直接誤判？有辦法向產線工程師合理解釋嗎？"),

    dict(id="alfa", name="誠釱科技股份有限公司", brand="ALFA", booth="A0507a",
         zone="世貿一館 AI機器人區", priority=2, theme="主題一",
         core="自動化整廠設備 + IIoT 解決方案",
         tags=["SmartManufacturing","IIoT"],
         tech="自動化整廠設備與工業物聯網整合商，擅長 PLC 數據採集與設備自動化。",
         pinn="【傳統硬體規則限制】主要依賴 IT/OT 整合與傳統門檻值控制，AI 多用於預測性維護，非 PINN 模型。",
         osat="中等", osat_detail="具備高階製造業整廠自動化經驗，但 AI 自研比例需現場確認。",
         kq="你們的 IIoT 方案在介接 OSAT 客戶現有的 MES 系統時，是透過公有標準協定（如 SECS/GEM），還是需要客製化 API？"),

    dict(id="sinyu", name="信宇科技股份有限公司", brand="SIN YU", booth="A0907a",
         zone="世貿一館 AI機器人區", priority=1, theme="主題一",
         core="機械手臂 / SmartManufacturing",
         tags=["AI","Robotics","SmartManufacturing"],
         tech="機械手臂整合、多軸運動控制與智慧製造系統集成。",
         pinn="【運動學物理約束】機械手臂的運動軌跡控制基於強烈的運動學與物理方程，是最天然的物理約束，但非神經網路 PINN。",
         osat="中等", osat_detail="主要負責產線後段包裝、搬運等機械手臂自動化整合。",
         kq="你們機械手臂的智慧路徑規劃，目前有導入任何基於強化學習（RL）的 AI 模型嗎？還是純傳統控制工程？"),

    dict(id="twtmc", name="台灣協力測控系統股份有限公司", brand="—", booth="A1015a",
         zone="世貿一館 AI機器人區", priority=1, theme="主題一",
         core="機械手臂 + 工業物聯網解決方案",
         tags=["Robotics","IIoT"],
         tech="工業量測、自動化光學檢測（AOI）與多軸機械手臂整合方案。",
         pinn="【精密幾何量測】核心是精密的物理量測與光學干涉分析，AI 用於視覺輔助分類。",
         osat="高", osat_detail="在晶圓檢測、高階 PCB 與載板檢測有深厚硬體設備落地實績。",
         kq="在高精密封裝（如 CoWoS）的 3D 量測上，你們的視覺 AI 如何與物理光學干涉數據做融合（Data Fusion）？"),

    dict(id="ability", name="佳能企業股份有限公司", brand="Ability", booth="(現場確認)",
         zone="世貿一館 AI機器人區", priority=2, theme="主題一",
         core="影像處理硬體 / 智慧 IPC / Edge Vision OS",
         tags=["AI","EdgeAI","ComputerVision"],
         tech="影像處理硬體、智慧 IPC 與嵌入式視覺模組（Edge Vision OS），強項在邊緣端影像硬體開發。",
         pinn="【硬體邊緣推理】不負責上層 PINN 演算法，而是提供演算法跑得動的硬體平台。",
         osat="中等", osat_detail="提供視覺感測模組給其他半導體自動化設備商，屬供應鏈層。",
         kq="如果我們團隊自己用 Python 寫了製造業的 AI 預測模型，可以直接編譯並布署到你們的智慧相機晶片上嗎？"),

    dict(id="uoster", name="優士特精密科技股份有限公司", brand="—", booth="(現場確認)",
         zone="世貿一館 AI機器人區", priority=2, theme="主題一",
         core="高精度精密導軌 / 線性馬達 / 定位模組",
         tags=["SmartManufacturing","精密硬體"],
         tech="高精度自動化精密導軌、線性馬達與定位模組供應商。純粹的硬體物理底座，無軟體 AI 模型。",
         pinn="【純硬體物理極限】沒有軟體 AI 模型，但硬體精度決定了 AI 控制演算法的上限。",
         osat="高", osat_detail="半導體挑揀機、封裝機台內部所需的高精度位移零組件供應商。",
         kq="面對 OSAT 廠微米級的點膠或打線需求，你們的精密模組在高速連續作動下的物理磨損與溫飄，數據有開放給外部 AI 做預測嗎？"),

    # ── 主題二：自學習 AI Agent ─────────────────────────────────────────────
    dict(id="corelink", name="新加坡商芯夥科技台灣分公司", brand="—", booth="A0912",
         zone="世貿一館 AI機器人區", priority=3, theme="主題二",
         core="Edge AI 晶片架構與軟硬整合",
         tags=["AI","DataCenter","EdgeAI","GenerativeAI","LLM"],
         tech="Edge AI 晶片架構與軟硬整合，聚焦邊緣端 AI 推論加速。具體底層技術架構待現場確認。",
         pinn="【待現場驗證】需確認邊緣晶片是否支援地端即時微調（Fine-tuning），或僅能執行靜態推理。Federated Learning 能力是關鍵驗證點。",
         osat="偏低", osat_detail="拓荒階段，邊緣 AI 在製造業的自學習落地案例待現場確認。",
         kq="你們的 Edge AI 方案在邊緣端是單純執行推論，還是具備 Federated Learning（聯邦學習）的能力來自我更新？"),

    dict(id="skymizer", name="臺灣發展軟體科技股份有限公司", brand="Skymizer", booth="R0923",
         zone="南港二館 AI運算系統區", priority=3, theme="主題二",
         core="自研 LISA 指令集 / HTX301 推論晶片 / 700B 地端模型",
         tags=["AI","AI Platform","EdgeAI","LLM"],
         tech="自研 LISA 指令集與專攻 Decode 階段的 HTX301 推論晶片；單卡支援 384GB 記憶體，可跑 700B 超大模型。支援 OpenClaw 等 Agent 框架進行地端自主算力部署。",
         pinn="【地端算力防幻覺】單卡 384GB 記憶體在地端跑 700B 超大模型，透過封閉環境與私有數據輸入，從根本消除依賴雲端產生幻覺與洩密風險，不依賴 RLHF 而是從架構層解決。",
         osat="高", osat_detail="鎖定 IC 設計、軟體工程（Code Copilot）與金融業的地端自主算力需求，提供可完全私有化的 AI 基礎算力設施。",
         kq="你們的 HTX301 晶片在處理多 Agent 協同作業（Multi-Agent）時，KV-cache 在節點間傳遞的延遲表現能否取代現有 GPU 方案？"),

    dict(id="nuwa", name="人機互動場域方案主題館", brand="Nuwa Robotics（女媧創造）/ Vyin AI", booth="A0509a",
         zone="世貿一館 AI機器人區", priority=2, theme="主題二",
         core="Embodied AI / 實體機器人載體 + 多模態互動",
         tags=["AI","AI Platform","AI Service","Robotics"],
         tech="集合 Nuwa Robotics（女媧創造）與 Vyin AI 的實體載體展示區，展示 Embodied AI 整合方案，涵蓋語音、視覺、肢體動作的多模態互動系統。",
         pinn="【實體多模態互動限制】透過機器人軀體（Embodied AI）將 AI 應答與物理動作（視線追蹤、肢體語言）綁定，利用現實物理邊界減少虛擬文本的發散幻覺，而非依賴純文字 RLHF。",
         osat="高", osat_detail="主要落地於餐飲導覽、醫療照護、教育互動等需實體互動的商業場景，服務型機器人部署案例豐富。",
         kq="實體機器人若要在吵雜的工廠或展場環境下精準辨識語意並進行自學習，你們在降噪與語音自適應演算法上做了什麼底層優化？"),

    dict(id="vyin", name="遊戲橘子數位科技", brand="Vyin AI / VyinRIS", booth="A0509a",
         zone="世貿一館 AI機器人區", priority=2, theme="主題二",
         core="VyinRIS 機器人大腦 / 企業級 AI Agent / 智慧零售",
         tags=["AI","AI Service","Robotics"],
         tech="首次發布 VyinRIS（Robotic Intelligence Solution）機器人大腦，主打企業級 AI Agent；聚焦智慧零售場景，將線下消費者行為結構化為 Agent 決策訓練數據。",
         pinn="【實體數據動態學習】將線下場域中顧客的詢問、猶豫等微小訊號結構化提煉為數據洞察，用以動態修正 Agent 的應對邏輯與銷售策略，形成閉環自學習迴路。",
         osat="中等", osat_detail="專注於智慧零售與藥局場景，預計今年下半年完成台灣市場多個連鎖體系的 PoC 驗證，實際落地案例待確認。",
         kq="VyinRIS 收集到的線下消費者決策軌跡，是否能與企業現有的 CDP（顧客數據平台）或 ERP 系統進行無縫即時雙向串接？"),

    dict(id="kneron", name="耐能智慧股份有限公司", brand="Kneron", booth="R0532",
         zone="南港二館 AI運算系統區", priority=2, theme="主題二",
         core="自研 KL 系列可重構 NPU / KneoEdge 企業 AI 基礎設施",
         tags=["AI","AI Platform","AMR","AutonomousVehicles","EdgeAI"],
         tech="具可重構特性的自研 NPU 架構（KL 系列），整合 KneoEdge 企業 AI 基礎設施；推動「在地化 AI 助理」，支援視覺、雷達、紅外線等多模態感測器輸入。",
         pinn="【物理感測數據收斂】直接接收視覺、雷達、紅外線等真實世界物理訊號，將生成式 AI 限縮在確定性極高的物理邊界內，從感測器層防範幻覺發散。",
         osat="高", osat_detail="在智慧交通（DMS 駕駛偵測）、3D 人臉門禁與企業會議助理（KneoMeet）有明確的邊緣落地實例，NPU 架構已通過多項車規認證。",
         kq="當 Edge 端的 AI Agent 遇到無法辨識的邊緣案例（Corner Case）時，你們的系統是如何將回饋數據拋回雲端進行自我修正，並同步更新邊緣端模型的？"),

    # ── 主題三：自動化工作流（n8n 類） ─────────────────────────────────────
    dict(id="airpa", name="聯剛科技股份有限公司", brand="AiRPA / ARAID / PLC PLUS", booth="R0134",
         zone="南港二館 AI運算系統區", priority=3, theme="主題三",
         core="自研 AiRPA 平台 / AI 視覺 + OCR/LLM 流程編排",
         tags=["DataCenter","EdgeAI","Robotics","SmartManufacturing"],
         tech="自研 AiRPA 平台，將傳統 RPA 流程編排整合 AI 視覺與文本識別（OCR/LLM），專為工廠自動化流程串接設計，是本次展會最接近「n8n for manufacturing」的標的。",
         pinn="【ERP/MES 串接極高】專為工廠自動化設計，支援原生介接各家 ERP 與主流 MES 系統；RPA 本質是規則型自動化，結合 AI 做例外處理，流程邏輯透明，可解釋性高。",
         osat="中等", osat_detail="主要在中央伺服器或智慧網關（Gateway）執行流程調度，地端邊緣算力依賴外部硬體；Edge AI 支援度中等。",
         kq="你們的 AiRPA 在串接 OSAT 廠特有的舊型 PLC 或不開放 API 的封閉 MES 時，主要靠視覺模擬操作（無頭瀏覽器），還是有原生底層驅動？"),

    dict(id="yonyou", name="台灣用友資訊軟體有限公司", brand="—", booth="R0325a",
         zone="南港二館 AI運算系統區", priority=3, theme="主題三",
         core="YonBIP 企業級雲服務平台 / MaaS 架構",
         tags=["AI Platform","Cloud","MaaS","SI"],
         tech="基於用友 YonBIP 企業級雲服務平台與 MaaS（模型即服務）架構，整合 AI 分析與 ERP 核心業務流程；自身就是亞洲頂級 ERP 大廠，底層數據架構極強。",
         pinn="【ERP/MES 串接極高】自身是 ERP 大廠，與 ERP 的串接是母廠優勢；但 MaaS 架構高度核心化、雲端化，非為產線微秒級反應設計。",
         osat="偏低", osat_detail="架構並非專為 Edge AI 微秒級即時反應設計；若需完全 Local 化地端布署（如黃光區斷網環境），需額外確認可行性。",
         kq="如果 OSAT 客戶希望在完全斷網的地端機台（黃光/封裝區）布署你們的工作流進行即時生產調度，用友的 MaaS 能完全 Local 化嗎？"),

    dict(id="aptbee", name="儒毅科技股份有限公司", brand="AptBee", booth="R0731",
         zone="南港二館 AI運算系統區", priority=2, theme="主題三",
         core="智慧製造 SI / 客製化 AI Service / 異質系統整合",
         tags=["AI Platform","AI Service","Cloud","SI","SmartManufacturing"],
         tech="智慧製造與大數據系統整合（SI）服務，提供客製化 AI Service；作為 SI 商，彈性取決於客戶預算，擅長用專案方式打通 MES 與 ERP，可協助封裝布署 AI 模型至地端。",
         pinn="【ERP/MES 串接高（客製化專案）】彈性極強的 SI 商，可用專案方式打通各種異質系統；但整合深度取決於客戶預算，非標準化產品。",
         osat="中等", osat_detail="依專案需求客製化布署，可協助將 AI 模型封裝布署至地端；Edge AI 支援度中等，彈性依案子而定。",
         kq="面對製造業流程自動化，你們是推薦客戶買斷現成的視覺化編排工具（如 n8n），還是完全由你們代工硬編碼（Hard-coded）開發？"),

    dict(id="arbor", name="磐儀科技股份有限公司", brand="ARBOR / AMobile", booth="P0713",
         zone="南港二館 工業物聯網區", priority=2, theme="主題三",
         core="IIoT 硬體平台 / 行動智慧 / 廠務端軟硬整合",
         tags=["AI Platform","ComputerVision","EdgeAI","IIoT"],
         tech="工業物聯網（IIoT）硬體平台，結合行動智慧、車載運算及廠務端軟硬整合方案；強項在 OT 端（機台、感測器）的數據採集與 IIoT 平台整合。",
         pinn="【ERP/MES 串接中等】強項在 OT 端數據採集；向上介接 IT 端（ERP）通常需透過標準網關，非直接 ERP 串接強項，但硬體生態系完整。",
         osat="極高", osat_detail="本身提供高規工業級嵌入式晶片與強固型設備，是自動化工作流地端化運算的完美 Edge AI 載體；Edge AI 支援度極高。",
         kq="你們的 IIoT 平台（AMobile 方案）是否內建支援 Node-RED 或類似的視覺化工作流引擎？對 SECS/GEM 協定的支援度如何？"),

    dict(id="iei", name="威強電工業電腦股份有限公司", brand="IEI", booth="P0114",
         zone="南港二館 工業物聯網區", priority=2, theme="主題三",
         core="工業電腦（IPC）硬體架構 / AI 加速卡整合",
         tags=["AI Platform","Edge","EdgeAI","SmartManufacturing"],
         tech="工業電腦（IPC）硬體架構，近年主打結合 AI 加速卡（顯卡、VPU）的智慧製造解決方案；硬體專為 Edge AI 推理設計，能頂住工廠惡劣環境的高溫與震動。",
         pinn="【ERP/MES 串接中等】提供硬體底座，軟體串接通常交由合作 SI 商負責，非 ERP 整合主力；但硬體生態系成熟，搭配 SI 可完整落地。",
         osat="極高", osat_detail="核心強項在 Edge AI 硬體，專為惡劣環境設計；最新機型支援多工（機器視覺 + 流程自動化編排）同時運行，CPU/GPU 資源分配待確認。",
         kq="你們最新的 Edge AI 工業電腦在跑多工（同時處理機器視覺瑕疵檢測與現場流程自動化編排）時，系統底層如何配置 CPU/GPU 資源以防當機？"),

    dict(id="adlink", name="凌華科技股份有限公司", brand="ADLINK", booth="P0425a",
         zone="南港二館 工業物聯網區", priority=2, theme="主題三",
         core="工業 AI 整合平台 / DDS 高頻數據傳輸 / OT 層設備串接",
         tags=["IIoT","EdgeAI","AI Platform"],
         tech="工業電腦重量級大廠，工業 AI 整合平台核心基於 DDS（資料分散服務）高頻數據傳輸技術；在工廠 OT 層設備串接無人能敵，能將機台高頻數據即時結構化。",
         pinn="【ERP/MES 串接極高（OT 層）】在工廠 OT 層設備串接能力最強；DDS 技術支援非同步資料交換，向上對接 IT 層 ERP/MES 路徑清晰，是整廠整合的理想基礎。",
         osat="極高", osat_detail="結合 Intel/NVIDIA 邊緣運算技術，是台灣智慧工廠 Edge AI 頭部玩家；在半導體測試設備（ATE）領域有深厚客戶基礎。",
         kq="你們的工業 AI 整合平台在介接高階半導體封裝設備時，DDS 技術如何與 IT 層的 ERP/MES 工作流進行非同步（Async）的資料交換？"),

    dict(id="lex", name="博來科技股份有限公司", brand="LEX SYSTEM", booth="P1213",
         zone="南港二館 工業物聯網區", priority=1, theme="主題三",
         core="緊湊型/無風扇嵌入式系統 / 工業母機主機板",
         tags=["AI Platform","EdgeAI","IIoT","SmartManufacturing"],
         tech="專精緊湊型（Compact）、無風扇嵌入式系統與工業母機主機板設計；體積小、功耗低，極度適合直接鎖在機械手臂或 OSAT 挑揀機台內做極端邊緣運算。",
         pinn="【ERP/MES 串接中等】純硬體元件與嵌入式系統供應商，無軟體 ERP 串接能力，需搭配軟體 SI 商；定位為極端邊緣的計算載體。",
         osat="極高", osat_detail="極端邊緣運算載體，體積小、功耗低，適合直接內嵌於 OSAT 挑揀機台；可支援 Docker/K8s 邊緣版大量布署自動化工作流鏡像（待確認）。",
         kq="面對智慧工廠的多節點布署，你們的嵌入式系統是否有支援 Docker 或 K8s 邊緣版，方便大量布署自動化工作流鏡像（Image）？"),

    dict(id="fanuc", name="世紀貿易股份有限公司", brand="FANUC（台灣代理）", booth="(現場確認)",
         zone="世貿一館 AI機器人區", priority=2, theme="主題三",
         core="FANUC 工業機器人 / 整廠自動化設備整合",
         tags=["Robotics","SmartManufacturing","自動化整廠"],
         tech="全球工業機器人巨頭 FANUC 在台重要代理商，專攻自動化整廠設備整合；FANUC 系統自成一格（FOCAS 協定），在機台控制與自動化加工流程編排上具有絕對控制權。",
         pinn="【ERP/MES 串接高（設備控制層）】FANUC 在機台控制與自動化加工流程編排具絕對控制權；但系統封閉性高，向上對接 IT/ERP 層需透過 FOCAS 特定介面，開放程度有限。",
         osat="極高", osat_detail="機械手臂內部配備強大的專用運動控制器，可即時處理路徑規劃；Edge AI 計算能力極強，是工廠邊緣控制的最終執行層。",
         kq="發那科（FANUC）目前的控制器，如何開放底層數據給第三方 AI Agent 或類似 n8n 的開源工作流工具進行即時控制下控？"),

    # ── 補充：半導體 / OSAT 相關 ────────────────────────────────────────────
    dict(id="nxp", name="恩智浦半導體", brand="NXP", booth="A0803",
         zone="世貿一館 AI機器人區", priority=2, theme="補充",
         core="IC 設計（工業機器人控制晶片）",
         tags=["AI","IC設計","工業控制"],
         tech="IC 設計，廣泛用於工業機器人控制與工廠自動化晶片，提供即時控制 MCU。",
         pinn="【工業控制 IC】提供晶片級的實時控制能力，是工廠 AI 控制的硬體底座。",
         osat="高", osat_detail="晶片廣泛應用於工廠自動化控制器，OSAT 設備常見。",
         kq="你們的工業控制晶片，對於整合 PINN 等 AI 推理工作負載，有沒有專用加速器（NPU）方案？"),

    dict(id="ti", name="德州儀器", brand="TI", booth="A1026",
         zone="世貿一館 AI機器人區", priority=2, theme="補充",
         core="機械手臂微控制器 / 工業自動化基礎晶片",
         tags=["AI","工業MCU","自動化"],
         tech="機械手臂微控制器，工業自動化基礎晶片供應商，提供精確實時控制 MCU 與感測器介面。",
         pinn="【微控制器層】提供精確的實時控制晶片，是工廠自動化的基礎硬體。",
         osat="高", osat_detail="TI MCU 廣泛用於打線機、封裝機等 OSAT 設備控制板。",
         kq="你們的工業 MCU 系列，有沒有支援邊緣 AI 推理的型號，以及對應的 SDK 或開發套件？"),

    dict(id="simo", name="慧榮科技", brand="Silicon Motion", booth="G0001",
         zone="半導體及先進技術區", priority=1, theme="補充",
         core="Flash Controller IC（OSAT 相關）",
         tags=["半導體","IC設計","OSAT"],
         tech="Flash controller IC 設計，OSAT 封裝相關，是儲存晶片控制器全球主要供應商。",
         pinn="【半導體 IP】核心業務為儲存晶片控制器，AI 應用偏向設計 EDA 工具優化。",
         osat="高", osat_detail="Flash controller 是 OSAT 封裝測試的核心晶片之一。",
         kq="你們的 Flash controller 在高速封裝測試（ATE）的品質管控上，有沒有導入 AI 品質預測系統？"),

    dict(id="neousys", name="宸曜科技", brand="Neousys", booth="R0129",
         zone="南港二館 AI運算系統區", priority=2, theme="補充",
         core="工業 AI 電腦平台（多路 GPU 推理）",
         tags=["AI","EdgeAI","工業電腦"],
         tech="工業 AI 電腦平台，支援多路 GPU 推理，專為工廠 Edge AI 環境優化，耐震耐溫設計。",
         pinn="【Edge AI 運算平台】提供高性能工業邊緣 AI 運算硬體，可支援複雜 AI 模型包括 PINN。",
         osat="中等", osat_detail="高性能工業電腦，可作為 PINN 推理的邊緣運算節點。",
         kq="你們的工業 AI 電腦，支援在 OSAT 廠的電磁干擾（EMI）環境下穩定運行嗎？有認證文件嗎？"),

    dict(id="ibase", name="廣積科技", brand="IBASE", booth="P0526",
         zone="南港二館 工業物聯網區", priority=1, theme="補充",
         core="EdgeAI 嵌入式平台",
         tags=["EdgeAI","嵌入式","AI Platform"],
         tech="EdgeAI 嵌入式平台，支援 AI 推理加速的工業電腦模組，多種 AI 加速器整合。",
         pinn="【嵌入式 AI 平台】硬體模組供應商，支援多種 AI 加速器整合。",
         osat="中等", osat_detail="嵌入式模組供應商，適合工廠 AI 邊緣部署。",
         kq="你們的嵌入式平台，有沒有針對振動環境（如打線機台旁）的防震設計認證？"),

    dict(id="cincoze", name="德承股份有限公司", brand="Cincoze", booth="Q0401a",
         zone="南港二館 工業物聯網區", priority=1, theme="補充",
         core="EdgeAI + Embedded 工業電腦（寬溫高耐用）",
         tags=["EdgeAI","Embedded","工業電腦"],
         tech="EdgeAI + Embedded 工業電腦，強調寬溫（-40~70°C）與高耐用性設計，適合惡劣環境。",
         pinn="【工業邊緣硬體】提供惡劣環境下穩定運行的工業電腦，AI 軟體由客戶自行整合。",
         osat="中等", osat_detail="高耐用工業電腦，適合半導體廠無塵室部署。",
         kq="你們的 Edge AI 電腦，能夠在 OSAT 廠的高溫無塵室（35°C+）環境下長時間穩定運行嗎？"),
]

# ── Session state 初始化 ────────────────────────────────────────────────────
for v in VENDORS:
    vid = v["id"]
    for field in ("fee", "contact", "memo"):
        k = f"{field}_{vid}"
        if k not in st.session_state:
            st.session_state[k] = ""
    k_vis = f"visited_{vid}"
    if k_vis not in st.session_state:
        st.session_state[k_vis] = False

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 COMPUTEX 2026\n### 展會戰情儀表板")
    st.markdown("---")

    THEME_LABELS = {
        "主題一": "🔵 主題一：製造業AI/PINN",
        "主題二": "🟣 主題二：自學習AI Agent",
        "主題三": "🟢 主題三：工作流自動化",
        "補充":   "🟡 補充：半導體相關",
    }
    with st.expander("📌 展示主題", expanded=True):
        sel_themes = [t for t in THEME_LABELS
                      if st.checkbox(THEME_LABELS[t], value=True, key=f"theme_cb_{t}")]

    with st.expander("⭐ 優先等級", expanded=True):
        sel_prios = (
            ([3] if st.checkbox("★★★ 必訪", value=True, key="p3") else []) +
            ([2] if st.checkbox("★★  重要",  value=True, key="p2") else []) +
            ([1] if st.checkbox("★   備選",  value=True, key="p1") else [])
        )

    with st.expander("🏭 OSAT 落地實績", expanded=True):
        sel_osat = [lvl for lvl in ("極高", "高", "中等", "偏低")
                    if st.checkbox(lvl, value=True, key=f"osat_{lvl}")]

    with st.expander("🔍 搜尋 / 篩選", expanded=True):
        search_kw = st.text_input("關鍵字搜尋", placeholder="廠商 / 品牌 / 技術...",
                                  label_visibility="collapsed")
        only_vis  = st.checkbox("只顯示已拜訪", value=False)

    st.markdown("---")
    with st.expander("📤 匯出筆記", expanded=False):
        if st.button("📥 產生 JSON 報告", use_container_width=True):
            export = {
                "generated": datetime.now().isoformat(),
                "event": "COMPUTEX 2026",
                "vendors": [
                    {
                        "name": v["name"], "brand": v["brand"], "booth": v["booth"],
                        "theme": v["theme"], "osat": v["osat"],
                        "visited":  st.session_state.get(f"visited_{v['id']}", False),
                        "fee":      st.session_state.get(f"fee_{v['id']}", ""),
                        "contact":  st.session_state.get(f"contact_{v['id']}", ""),
                        "memo":     st.session_state.get(f"memo_{v['id']}", ""),
                        "killer_question": v["kq"],
                    }
                    for v in VENDORS
                ],
            }
            st.session_state["_export"] = json.dumps(export, ensure_ascii=False, indent=2)

        if "_export" in st.session_state:
            fname = f"computex2026_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            st.download_button(
                "💾 下載 JSON",
                data=st.session_state["_export"].encode("utf-8"),
                file_name=fname,
                mime="application/json",
                use_container_width=True,
            )

# ── 過濾 ─────────────────────────────────────────────────────────────────────
def match(v):
    if v["theme"] not in sel_themes:        return False
    if v["priority"] not in sel_prios:      return False
    if v["osat"] not in sel_osat:           return False
    if only_vis and not st.session_state.get(f"visited_{v['id']}", False): return False
    if search_kw:
        hay = " ".join([v["name"], v["brand"], v["core"],
                        v["tech"], v["pinn"], v["kq"],
                        " ".join(v["tags"])]).lower()
        if search_kw.lower() not in hay:    return False
    return True

filtered = [v for v in VENDORS if match(v)]

# ── 統計列 ───────────────────────────────────────────────────────────────────
st.markdown("# 🎯 COMPUTEX 2026 展會戰情儀表板")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("篩選廠商",    f"{len(filtered)}", f"/ {len(VENDORS)} 家")
m2.metric("★★★ 必訪",  sum(1 for v in filtered if v["priority"] == 3))
m3.metric("OSAT 高相關", sum(1 for v in filtered if v["osat"] in ("極高","高")))
m4.metric("已拜訪",      sum(1 for v in filtered
                             if st.session_state.get(f"visited_{v['id']}", False)))
m5.metric("已記錄筆記",  sum(1 for v in filtered
                             if any(st.session_state.get(f"{f}_{v['id']}", "")
                                    for f in ("fee","contact","memo"))))
st.markdown("---")

if not filtered:
    st.info("目前篩選條件無符合廠商，請調整左側篩選。")
    st.stop()

# ── 廠商卡片 ─────────────────────────────────────────────────────────────────
def star_str(n):
    return "★" * n + "☆" * (3 - n)

def render_card(v):
    vid  = v["id"]
    tc   = THEME_COLORS[v["theme"]]
    oc   = OSAT_COLORS.get(v["osat"], "#6b7280")
    vis  = "  ✅ 已拜訪" if st.session_state.get(f"visited_{vid}", False) else ""
    br   = f"【{v['brand']}】 " if v["brand"] not in ("—", "") else ""

    st.markdown(f"""
    <div class="vendor-card">
      <div class="card-header" style="background:{tc}">
        <span class="stars">{star_str(v['priority'])}</span>
        <div class="company-name">{v['name']}</div>
        <div class="brand-booth">{br}📍 {v['booth']}{vis}</div>
      </div>
      <div class="card-body">
        <span class="badge" style="background:{oc};color:white">OSAT {v['osat']}</span>
        <span class="badge"
              style="background:{tc}22;color:{tc};border:1px solid {tc}44">{v['theme']}</span>
        <div style="font-size:12px;color:#555;margin-bottom:6px">
          <b>核心：</b>{v['core']}
        </div>
        <div class="killer-q">
          <div class="kq-label">🎯 展場必殺提問</div>
          <div class="kq-text">{v['kq']}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander(f"🔬 技術細節 ｜ {v['name']}"):
        st.markdown(f"**技術架構：** {v['tech']}")
        st.markdown(f"**PINN / AI 評估：** {v['pinn']}")
        st.markdown(f"**OSAT 細節：** {v['osat_detail']}")
        tag_str = "  ".join(f"`{t}`" for t in v["tags"])
        st.markdown(f"**標籤：** {tag_str}")
        st.markdown(f"**展區：** {v['zone']}")

    cn1, cn2 = st.columns(2)
    with cn1:
        st.text_area("💰 收費模式",  key=f"fee_{vid}",     height=75,
                     placeholder="買斷 / 訂閱制 / 年費 / PoC 條件...")
    with cn2:
        st.text_area("👤 聯絡窗口",  key=f"contact_{vid}", height=75,
                     placeholder="姓名 / 職稱 / Email / 手機...")
    st.text_area("📝 現場備忘",      key=f"memo_{vid}",    height=60,
                 placeholder="Demo 觀察 / 技術亮點 / 待跟進事項...")
    st.checkbox("✅ 標記為已拜訪",   key=f"visited_{vid}")
    st.markdown("<hr class='card-sep'>", unsafe_allow_html=True)

col_l, col_r = st.columns(2)
for i, v in enumerate(filtered):
    with (col_l if i % 2 == 0 else col_r):
        render_card(v)
