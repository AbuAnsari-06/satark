import React from "react";
import { AlertTriangle, CheckCircle2, Sparkles } from "lucide-react";
import { translations } from "../i18n";

const SAMPLE_MESSAGES = [
  // 4 SCAMS
  {
    id: "sample-kyc",
    type: "scam",
    title: {
      en: "Fake SBI KYC (Hinglish)",
      hi: "फर्जी SBI KYC (हिंग्लिश)",
    },
    text: "Dear customer, your SBI account band ho jayega today. Update KYC turant: http://sbi-kyc-update.xyz",
  },
  {
    id: "sample-loan",
    type: "scam",
    title: {
      en: "Instant Loan Approval",
      hi: "तत्काल लोन स्वीकृति",
    },
    text: "Congratulations! Your instant pre-approved personal loan of Rs 5,00,000 is ready for disbursal. Click to claim immediately: http://bit.ly/loan392",
  },
  {
    id: "sample-lottery",
    type: "scam",
    title: {
      en: "Lottery Prize with Fee",
      hi: "लॉटरी पुरस्कार (शुल्क मांग)",
    },
    text: "Dear winner, you won KBC lucky draw of Rs 25,00,000! Deposit small processing fee of Rs 1,500 to release your prize cheque. Call 9876543210",
  },
  {
    id: "sample-electricity",
    type: "scam",
    title: {
      en: "Electricity Bill Threat",
      hi: "बिजली काटने की धमकी",
    },
    text: "Dear consumer, your electricity power will be disconnected tonight at 9:30 PM by electricity office due to unpaid bill. Call electricity officer immediately: 9876543210",
  },

  // 4 GENUINE
  {
    id: "sample-bank-otp",
    type: "genuine",
    title: {
      en: "Real Bank OTP Alert",
      hi: "बैंक OTP डिलीवरी अलर्ट",
    },
    text: "482910 is your secret OTP for transaction of Rs 2,499.00 at Amazon Pay. Valid for 10 mins. Do not share this OTP with anyone. - State Bank of India",
  },
  {
    id: "sample-courier",
    type: "genuine",
    title: {
      en: "Courier Delivery Update",
      hi: "अमेज़न डिलीवरी अपडेट",
    },
    text: "Your Amazon order #402-8392102 has been dispatched via BlueDart and is out for delivery today. Track your courier: https://amazon.in/orders",
  },
  {
    id: "sample-upi",
    type: "genuine",
    title: {
      en: "UPI Credit Alert",
      hi: "UPI क्रेडिट अलर्ट",
    },
    text: "Rs 1,500.00 credited to your HDFC Bank A/C ending in 4521 via UPI from Rahul Sharma. UPI Ref: 409218291045.",
  },
  {
    id: "sample-food-otp",
    type: "genuine",
    title: {
      en: "Swiggy Login OTP",
      hi: "Swiggy लॉगिन OTP",
    },
    text: "584920 is your OTP to log in to Swiggy. Valid for 5 minutes. Never share your OTP with anyone.",
  },
];

export default function SampleChips({ onSelectSample, lang }) {
  const t = translations[lang] || translations.en;

  const scamSamples = SAMPLE_MESSAGES.filter((s) => s.type === "scam");
  const genuineSamples = SAMPLE_MESSAGES.filter((s) => s.type === "genuine");

  return (
    <div className="pt-2 border-t border-slate-200/70">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 mb-3">
        <Sparkles className="w-3.5 h-3.5 text-blue-500" />
        <span>{t.sampleHeading}</span>
      </div>

      <div className="space-y-2.5">
        {/* Scam category chips */}
        <div>
          <div className="flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider text-rose-700 mb-1.5">
            <AlertTriangle className="w-3 h-3 text-rose-500" />
            <span>{t.sampleScams}</span>
          </div>
          <div className="flex flex-wrap gap-1.5 sm:gap-2">
            {scamSamples.map((sample) => (
              <button
                key={sample.id}
                id={sample.id}
                type="button"
                onClick={() => onSelectSample(sample.text)}
                className="px-2.5 py-1 text-xs font-medium rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-800 border border-rose-200/80 transition-all cursor-pointer active:scale-95 text-left"
              >
                {sample.title[lang] || sample.title.en}
              </button>
            ))}
          </div>
        </div>

        {/* Genuine category chips */}
        <div>
          <div className="flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider text-emerald-700 mb-1.5">
            <CheckCircle2 className="w-3 h-3 text-emerald-500" />
            <span>{t.sampleGenuine}</span>
          </div>
          <div className="flex flex-wrap gap-1.5 sm:gap-2">
            {genuineSamples.map((sample) => (
              <button
                key={sample.id}
                id={sample.id}
                type="button"
                onClick={() => onSelectSample(sample.text)}
                className="px-2.5 py-1 text-xs font-medium rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200/80 transition-all cursor-pointer active:scale-95 text-left"
              >
                {sample.title[lang] || sample.title.en}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
