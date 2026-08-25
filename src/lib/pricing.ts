export interface PricingPlan {
  id: "single" | "pro" | "agency";
  name: string;
  price: string;
  period?: string;
  tagline: string;
  features: string[];
  cta: string;
  available: boolean;
  highlight?: boolean;
}

/** Single source of truth for pricing. Change values here only. */
export const PRICING_PLANS: PricingPlan[] = [
  {
    id: "single",
    name: "Free — Single Page",
    price: "$0",
    period: "/mo",
    tagline: "Audit any single URL with the full RankX engine.",
    features: [
      "Single URL SEO scan",
      "SEO score & grade",
      "SEO issues with recommendations",
      "AI recommendations",
      "Metadata analysis",
      "Basic report download",
    ],
    cta: "Available now",
    available: true,
  },
  {
    id: "pro",
    name: "Pro — Multi-Page",
    price: "$29",
    period: "/mo",
    tagline: "Crawl an entire website, not just one page.",
    features: [
      "Everything in Single Page",
      "Multi-page website crawling",
      "Crawl multiple URLs in one run",
      "Sitemap analysis",
      "Cross-page SEO analysis",
      "Full website report",
      "Advanced media analysis",
    ],
    cta: "Upgrade Plan",
    available: false,
    highlight: true,
  },
  {
    id: "agency",
    name: "Agency",
    price: "Custom",
    tagline: "For agencies auditing many client sites.",
    features: [
      "Everything in Pro",
      "Unlimited crawl volume",
      "Team workspaces",
      "White-label reports",
      "API access",
      "Priority support",
    ],
    cta: "Contact sales",
    available: false,
  },
];

export const MULTI_PAGE_LOCKED_NOTE =
  "Multi-page crawling requires a subscription. It is not part of the free single-page scan.";
