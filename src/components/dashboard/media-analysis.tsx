import { useState } from "react";
import { Images, ImageOff, Film, X } from "lucide-react";
import type { MediaResult, ScannerResponse } from "@/types/scan";
import { DashboardSection } from "./section";
import { EmptyState } from "./empty-state";

function text(input?: string): string | null {
  const trimmed = input?.trim();
  return trimmed ? trimmed : null;
}

export function MediaAnalysis({
  scan,
  media,
}: {
  scan: ScannerResponse;
  media?: MediaResult;
}) {
  const [lightbox, setLightbox] = useState<string | null>(null);
  const ogImage = text(scan["og:image"]);
  const twitterImage = text(scan.twitter_image);
  const images = media?.images ?? [];
  const videos = media?.videos ?? [];

  return (
    <DashboardSection
      icon={Images}
      title="Media Analysis"
      description="Image and video signals returned by the scan API."
    >
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-2xl border border-border bg-secondary/40 p-4">
          <div className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Total Images
          </div>
          <div className="mt-2 text-3xl font-bold tracking-tight text-foreground">{scan.images}</div>
        </div>
        <div className="rounded-2xl border border-border bg-secondary/40 p-4">
          <div className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Images Missing Alt
          </div>
          <div
            className={`mt-2 text-3xl font-bold tracking-tight ${
              scan.missing_alt > 0 ? "text-destructive" : "text-[color:var(--success)]"
            }`}
          >
            {scan.missing_alt}
          </div>
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        {[
          { label: "Open Graph Image", src: ogImage },
          { label: "Twitter Image", src: twitterImage },
        ].map(({ label, src }) => (
          <div key={label} className="overflow-hidden rounded-2xl border border-border">
            <div className="border-b border-border bg-secondary/50 px-4 py-2.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              {label}
            </div>
            {src ? (
              <button
                type="button"
                onClick={() => setLightbox(src)}
                className="block w-full"
                aria-label={`Open ${label} at full size`}
              >
                <img
                  src={src}
                  alt={label}
                  loading="lazy"
                  className="aspect-[1.91/1] w-full bg-secondary object-cover transition hover:opacity-90"
                />
              </button>
            ) : (
              <div className="flex aspect-[1.91/1] w-full flex-col items-center justify-center gap-2 bg-secondary/60 text-muted-foreground">
                <ImageOff className="h-6 w-6" />
                <span className="text-xs font-medium">No {label.toLowerCase()} found</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {images.length > 0 && (
        <div className="mt-8">
          <h3 className="mb-3 text-sm font-semibold text-foreground">Image Gallery</h3>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
            {images.map((image) => (
              <figure key={image.url} className="overflow-hidden rounded-2xl border border-border">
                <button
                  type="button"
                  onClick={() => setLightbox(image.url)}
                  className="block w-full"
                  aria-label={`Open image ${image.alt || image.url}`}
                >
                  <img
                    src={image.url}
                    alt={image.alt || ""}
                    loading="lazy"
                    className="aspect-square w-full bg-secondary object-cover transition hover:opacity-90"
                  />
                </button>
                <figcaption className="space-y-1 p-3">
                  <p className="truncate text-xs text-muted-foreground" title={image.url}>
                    {image.url}
                  </p>
                  {image.alt ? (
                    <p className="text-xs text-foreground">{image.alt}</p>
                  ) : (
                    <span className="inline-block rounded-full bg-red-50 px-2 py-0.5 text-[11px] font-semibold text-red-700 ring-1 ring-red-200">
                      Missing alt
                    </span>
                  )}
                  {image.width && image.height && (
                    <p className="text-[11px] text-muted-foreground">
                      {image.width}×{image.height}
                    </p>
                  )}
                </figcaption>
              </figure>
            ))}
          </div>
        </div>
      )}

      <div className="mt-8">
        <h3 className="mb-3 text-sm font-semibold text-foreground">Videos</h3>
        {videos.length > 0 ? (
          <div className="grid gap-4 sm:grid-cols-2">
            {videos.map((video) => (
              <div key={video.url} className="overflow-hidden rounded-2xl border border-border">
                <video controls preload="none" poster={video.poster} className="w-full bg-black">
                  <source src={video.url} />
                  Your browser does not support the video tag.
                </video>
                {video.title && (
                  <p className="p-3 text-sm font-medium text-foreground">{video.title}</p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            compact
            icon={Film}
            title="Video data not available for this scan."
          />
        )}
      </div>

      {lightbox && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Image preview"
          className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/70 p-6 backdrop-blur-sm"
          onClick={() => setLightbox(null)}
        >
          <button
            type="button"
            onClick={() => setLightbox(null)}
            aria-label="Close image preview"
            className="absolute right-6 top-6 grid h-10 w-10 place-items-center rounded-full bg-white text-foreground shadow-lg"
          >
            <X className="h-5 w-5" />
          </button>
          <img
            src={lightbox}
            alt="Full size preview"
            className="max-h-full max-w-full rounded-2xl object-contain"
            onClick={(event) => event.stopPropagation()}
          />
        </div>
      )}
    </DashboardSection>
  );
}
