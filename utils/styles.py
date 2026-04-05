import streamlit.components.v1 as components

def inject_styles():
    """Inject shared dark-theme CSS into the parent Streamlit document."""
    components.html("""
<script>
(function() {
  if (parent.document.getElementById('tj-styles')) return;

  ['https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css',
   'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap'
  ].forEach(function(href) {
    var l = document.createElement('link');
    l.rel = 'stylesheet'; l.href = href;
    parent.document.head.appendChild(l);
  });

  var s = document.createElement('style');
  s.id = 'tj-styles';
  s.textContent = `
    html,body{font-family:'Outfit',sans-serif!important}
    #MainMenu,footer{visibility:hidden!important}
    .stDeployButton{display:none!important}
    .block-container{padding-top:.8rem!important;padding-bottom:1rem!important;max-width:100%!important}
    .stApp{background:#0d1117!important}

    section[data-testid="stSidebar"]{
      background:linear-gradient(180deg,#0f172a 0%,#1e293b 100%)!important;
      border-right:1px solid rgba(59,130,246,.2)!important;
    }
    section[data-testid="stSidebar"]>div{background:transparent!important}
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label{color:#94a3b8!important}
    section[data-testid="stSidebar"] [data-baseweb="select"]>div{
      background:rgba(255,255,255,.06)!important;
      border:1px solid rgba(148,163,184,.2)!important;
      border-radius:10px!important;color:#e2e8f0!important;
    }
    section[data-testid="stSidebar"] a{color:#94a3b8!important;text-decoration:none!important}

    .stButton>button{
      background:linear-gradient(135deg,#3b82f6,#2563eb)!important;
      color:white!important;border-radius:12px!important;border:none!important;
      font-weight:700!important;font-size:.95rem!important;
      box-shadow:0 4px 20px rgba(37,99,235,.4)!important;
      width:100%!important;padding:.65rem 1.4rem!important;
      transition:all .2s ease!important;
    }
    .stButton>button:hover{
      background:linear-gradient(135deg,#60a5fa,#3b82f6)!important;
      transform:translateY(-2px)!important;
      box-shadow:0 8px 30px rgba(37,99,235,.5)!important;
    }
    .stProgress>div>div>div>div{
      background:linear-gradient(90deg,#3b82f6,#8b5cf6)!important;
      border-radius:99px!important;
    }
    .stProgress>div>div{background:#1e293b!important;border-radius:99px!important}
    .stTextInput>div>div{
      background:rgba(255,255,255,.06)!important;
      border:1px solid rgba(148,163,184,.2)!important;
      border-radius:10px!important;
    }
    .stTextInput input{color:#e2e8f0!important;background:transparent!important}
    iframe{border-radius:14px!important}

    @keyframes shimmer{0%{background-position:-400% center}100%{background-position:400% center}}
    @keyframes heroFloat{0%,100%{transform:translateY(0) rotate(-2deg)}50%{transform:translateY(-12px) rotate(2deg)}}
    @keyframes fadeSlideUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
    @keyframes pulse-dot{0%,100%{box-shadow:0 0 0 0 rgba(16,185,129,.6)}50%{box-shadow:0 0 0 7px rgba(16,185,129,0)}}
    @keyframes pulse-dot-end{0%,100%{box-shadow:0 0 0 0 rgba(244,63,94,.6)}50%{box-shadow:0 0 0 7px rgba(244,63,94,0)}}
  `;
  parent.document.head.appendChild(s);
})();
</script>
""", height=0)
