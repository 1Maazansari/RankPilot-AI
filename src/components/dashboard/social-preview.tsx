import { Share2, ImageOff } from "lucide-react";
import type { ScannerResponse } from "@/types/scan";
import { DashboardSection } from "./section";
import { EmptyState } from "./empty-state";

function text(input?: string): string | null {
  const trimmed = input?.trim();
  return trimmed ? trimmed : null;
}

function PreviewCard({
  platform,
  title,
  description,
  image,
  meta,
}: {
  platform: string;
  title: string | null;
  description: string | null;
  image: string | null;
  meta: { label: string; value: string }[];
}) {
  return (
    <div className="overflow-hidden rounded-2xl border border-border bg-white">
      <div className="border-b border-border bg-secondary/50 px-4 py-2.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        {platform}
      </div>
      {image ? (
        <img
          src={image}
          alt={`${platform} preview image for ${title ?? "this page"}`}
          loading="lazy"
          className="aspect-[1.91/1] w-full bg-secondary object-cover"
        />
      ) : (
        <div className="flex aspect-[1.91/1] w-full flex-col items-center justify-center gap-2 bg-secondary/60 text-muted-foreground">
          <ImageOff className="h-6 w-6" />
          <span className="text-xs font-medium">No {platform} image found</span>
        </div>
      )}
      <div className="space-y-1.5 p-4">
        <p className="text-sm font-semibold text-foreground">
          {title ?? <span className="italic text-muted-foreground">No title tag</span>}
        </p>
        <p className="text-sm text-muted-foreground">
          {description ?? (
            <span className="italic">No description tag</span>
          )}
        </p>
        <dl className="mt-3 space-y-1 border-t border-border pt-3">
          {meta.map((item) => (
            <div key={item.label} className="flex gap-2 text-xs">
              <dt className="shrink-0 font-semibold text-muted-foreground">{item.label}</dt>
              <dd className="break-all text-foreground/80">{item.value || "Not Found"}</dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  );
}

export function SocialPreview({ scan }: { scan: ScannerResponse }) {
  const ogTitle = text(scan["og:title"]);
  const ogDescription = text(scan["og:description"]);
  const ogImage = text(scan["og:image"]);
  const ogUrl = text(scan["og:url"]);
  const ogType = text(scan["og:type"]);

  const twTitle = text(scan.twitter_title);
  const twDescription = text(scan.twitter_description);
  const twImage = text(scan.twitter_image);
  const twCard = text(scan.twitter_card);

  const hasAny =
    ogTitle || ogDescription || ogImage || ogUrl || ogType || twTitle || twDescription || twImage || twCard;

  return (
    <DashboardSection
      icon={Share2}
      title="Social / Open Graph"
      description="How this page appears when shared, based on the tags found."
    >
      {hasAny ? (
        <div className="grid gap-6 md:grid-cols-2">
          <PreviewCard
            platform="Open Graph"
            title={ogTitle}
            description={ogDescription}
            image={ogImage}
            meta={[
              { label: "og:url", value: ogUrl ?? "" },
              { label: "og:type", value: ogType ?? "" },
            ]}
          />
          <PreviewCard
            platform="Twitter"
            title={twTitle}
            description={twDescription}
            image={twImage}
            meta={[{ label: "twitter:card", value: twCard ?? "" }]}
          />
        </div>
      ) : (
        <EmptyState
          icon={Share2}
          title="No social tags found"
          description="This page has no Open Graph or Twitter card metadata."
        />
      )}
    </DashboardSection>
  );
}
