export interface PricingPlan {
  id: string;
  name: string;
  price: string;
  period?: string;
  tagline: string;
  features: string[];
  cta: string;
  available: boolean;
  highlight?: boolean;
}

/** Early access: all current features are free. */
export const PRICING_PLANS: PricingPlan[] = [
  {
    id: "early-access",
    name: "Early Access — Free",
    price: "$0",
    period: "/free",
    tagline: "All current BrandVizi features. No signup. No credit card. No paid plan.",
    features: [
      "Full SEO Audit",
      "SEO Score & Issues",
      "AI Recommendations",
      "AI SEO Copilot",
      "Multi-Page Audit",
      "SEO Reports",
      "All Current Features Included",
    ],
    cta: "Start Free Audit",
    available: true,
    highlight: true,
  },
];
