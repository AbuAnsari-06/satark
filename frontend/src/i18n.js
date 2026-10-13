/**
 * Bilingual localization dictionary for Satark.
 * Supports English ('en') and Hindi ('hi').
 */

export const translations = {
  en: {
    appTitle: "Satark",
    tagline: "Scam & Fraud Detection Assistant",
    privacyBadge: "Your message is analyzed in memory and never stored.",
    privacyShort: "Zero message retention",
    langToggle: "हिं",
    langAria: "Switch language to Hindi",
    
    // Input Card
    inputHeading: "Analyze Message or Screenshot",
    inputSubheading: "Paste any suspicious SMS, WhatsApp, or UPI notification to get an instant safety verdict.",
    textareaPlaceholder: "Paste suspicious message here (e.g., 'Dear customer, your SBI account will be blocked today. Update KYC: http://...')...",
    charCount: "characters",
    dropzoneTitle: "Drop screenshot here or",
    dropzoneBrowse: "browse files",
    dropzoneSub: "PNG, JPG, or WebP up to 5 MB",
    removeImage: "Remove screenshot",
    analyzeBtn: "Analyze Message",
    analyzingBtn: "Scanning for scams...",
    emptyError: "Please enter a message or upload a screenshot to analyze.",
    
    // Sample Chips
    sampleHeading: "Or test with real-world examples:",
    sampleScams: "Common Scams",
    sampleGenuine: "Genuine Messages",
    
    // Result Card
    resultsHeading: "Analysis Verdict",
    aiUnavailableNotice: "AI analysis unavailable, showing rule-based result only.",
    scoreLabel: "Risk Score",
    outOf100: "out of 100",
    
    verdictSafe: "Safe",
    verdictSuspicious: "Suspicious",
    verdictScam: "Likely Scam",
    
    verdictDescSafe: "No prominent scam indicators found. Always stay vigilant with unfamiliar senders.",
    verdictDescSuspicious: "Contains multiple concerning signals. Do not click links or share credentials.",
    verdictDescScam: "High probability of fraud. Immediate risk of financial loss or account compromise.",
    
    messageHeading: "Analyzed Message",
    highlightHint: "Suspicious trigger phrases are highlighted below",
    
    scoreBreakdownHeading: "How we got this score",
    rulesContrib: "Rule-Based Signals",
    aiContrib: "AI Multimodal Model",
    
    scamTypeHeading: "Scam Category",
    howItWorksHeading: "How this scam works",
    redFlagsHeading: "Detected Red Flags",
    
    linkInspectorHeading: "Link Inspector",
    linkTableUrl: "Target URL / Domain",
    linkTableShortener: "Shortener",
    linkTableTld: "Risky TLD",
    linkTableLookalike: "Brand Spoofing",
    linkTableRisk: "Risk Tier",
    yes: "Yes",
    no: "No",
    none: "None",
    
    explanationHeading: "Clear Explanation",
    nextStepsHeading: "Recommended Next Steps",
    
    familyAlertBtn: "Copy Family Alert",
    reportSummaryBtn: "Copy Cybercrime Summary",
    copiedToast: "Copied to clipboard!",
    
    // Footer
    resetBtn: "Check Another Message",
    docsLink: "API Documentation (/docs)",
    disclaimer: "Satark is a decision-support tool, not a guarantee of safety. When in doubt, contact your bank directly using the official phone number printed on the back of your card.",
    helplineTitle: "National Cyber Fraud Helpline",
    helplineNumber: "1930",
    portalLink: "cybercrime.gov.in",
  },
  
  hi: {
    appTitle: "सतर्क",
    tagline: "धोखाधड़ी व स्कैम पहचान सहायक",
    privacyBadge: "आपका संदेश केवल जांचा जाता है, कभी भी सुरक्षित (store) नहीं किया जाता।",
    privacyShort: "जीरो डेटा स्टोरेज",
    langToggle: "EN",
    langAria: "अंग्रेजी भाषा में बदलें",
    
    // Input Card
    inputHeading: "संदेश या स्क्रीनशॉट की जांच करें",
    inputSubheading: "किसी भी संदेहास्पद SMS, WhatsApp या UPI अलर्ट को यहाँ पेस्ट करें और तुरंत सुरक्षा परिणाम पाएं।",
    textareaPlaceholder: "यहाँ संदेहास्पद संदेश पेस्ट करें (उदा: 'प्रिय ग्राहक, आपका SBI खाता आज बंद हो जाएगा। KYC तुरंत अपडेट करें: http://...')...",
    charCount: "अक्षर",
    dropzoneTitle: "स्क्रीनशॉट यहाँ डालें या",
    dropzoneBrowse: "फाइल चुनें",
    dropzoneSub: "PNG, JPG, या WebP अधिकतम 5 MB",
    removeImage: "स्क्रीनशॉट हटाएं",
    analyzeBtn: "संदेश की जांच करें",
    analyzingBtn: "खतरे की जांच जारी है...",
    emptyError: "कृपया जांच के लिए कोई संदेश लिखें या स्क्रीनशॉट अपलोड करें।",
    
    // Sample Chips
    sampleHeading: "या इन वास्तविक नमूनों से जांचें:",
    sampleScams: "आम धोखाधड़ी संदेश",
    sampleGenuine: "असली व सुरक्षित संदेश",
    
    // Result Card
    resultsHeading: "जांच परिणाम",
    aiUnavailableNotice: "AI मॉडल अनुपलब्ध है, केवल नियम आधारित परिणाम दिखाए जा रहे हैं।",
    scoreLabel: "जोखिम स्कोर",
    outOf100: "100 में से",
    
    verdictSafe: "सुरक्षित (Safe)",
    verdictSuspicious: "संदेहास्पद (Suspicious)",
    verdictScam: "धोखाधड़ी (Likely Scam)",
    
    verdictDescSafe: "धोखाधड़ी के कोई बड़े लक्षण नहीं मिले। फिर भी अनजान संदेशों से सावधान रहें।",
    verdictDescSuspicious: "कई संदेहास्पद संकेत मिले हैं। किसी लिंक पर क्लिक न करें और कोई जानकारी न दें।",
    verdictDescScam: "धोखाधड़ी की अत्यधिक संभावना है। वित्तीय नुकसान या खाता हैक होने का बड़ा खतरा है।",
    
    messageHeading: "जांचा गया संदेश",
    highlightHint: "खतरे वाले शब्दों को नीचे हाइलाइट किया गया है",
    
    scoreBreakdownHeading: "यह स्कोर कैसे तय हुआ",
    rulesContrib: "नियम आधारित संकेत",
    aiContrib: "AI मॉडल विश्लेषण",
    
    scamTypeHeading: "धोखाधड़ी का प्रकार",
    howItWorksHeading: "यह धोखाधड़ी कैसे काम करती है",
    redFlagsHeading: "पाए गए खतरे के संकेत",
    
    linkInspectorHeading: "लिंक विश्लेषक (Link Inspector)",
    linkTableUrl: "वेबसाइट लिंक / डोमेन",
    linkTableShortener: "शॉर्टनर",
    linkTableTld: "संदेहास्पद TLD",
    linkTableLookalike: "नकली ब्रांड",
    linkTableRisk: "जोखिम स्तर",
    yes: "हाँ",
    no: "नहीं",
    none: "कोई नहीं",
    
    explanationHeading: "सरल व्याख्या",
    nextStepsHeading: "सुरक्षा के लिए ज़रूरी कदम",
    
    familyAlertBtn: "परिवार के लिए चेतावनी कॉपी करें",
    reportSummaryBtn: "शिकायत सारांश कॉपी करें",
    copiedToast: "क्लिपबोर्ड पर कॉपी हो गया!",
    
    // Footer
    resetBtn: "अन्य संदेश की जांच करें",
    docsLink: "API दस्तावेज़ (/docs)",
    disclaimer: "सतर्क केवल एक निर्णय-सहायक टूल है, सुरक्षा की पूर्ण गारंटी नहीं। किसी भी संदेह पर अपने बैंक कार्ड के पीछे दिए गए आधिकारिक नंबर पर ही संपर्क करें।",
    helplineTitle: "राष्ट्रीय साइबर क्राइम हेल्पलाइन",
    helplineNumber: "1930",
    portalLink: "cybercrime.gov.in",
  },
};
