export type ApiErrorKind =
  | "invalid_url"
  | "unavailable"
  | "timeout"
  | "server"
  | "network"
  | "malformed";

export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly title: string;
  readonly status?: number;

  constructor(kind: ApiErrorKind, title: string, message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.kind = kind;
    this.title = title;
    this.status = status;
  }
}

/** Maps an HTTP status from the BrandVizi API to a user-safe error. */
export function apiErrorFromStatus(status: number, detail?: string): ApiError {
  switch (status) {
    case 400:
    case 422:
      return new ApiError(
        "invalid_url",
        "Invalid URL",
        detail || "That address isn't a valid website URL. Check it and try again.",
        status,
      );
    case 503:
      return new ApiError(
        "unavailable",
        "Website unavailable",
        detail || "The website didn't respond. It may be offline or blocking automated requests.",
        status,
      );
    case 504:
      return new ApiError(
        "timeout",
        "Request timed out",
        detail || "The website took too long to respond. Try again in a moment.",
        status,
      );
    default:
      return new ApiError(
        "server",
        "Server error",
        detail || "The BrandVizi server couldn't complete this scan. Please try again.",
        status,
      );
  }
}

export const NETWORK_ERROR = () =>
  new ApiError(
    "network",
    "Can't reach the BrandVizi server",
    "Cannot connect to the BrandVizi AI server. Please make sure the backend is running and VITE_API_BASE_URL is correct.",
  );

export const MALFORMED_ERROR = () =>
  new ApiError(
    "malformed",
    "Unexpected report format",
    "The server returned an unexpected report format.",
  );

export function toApiError(error: unknown): ApiError {
  if (error instanceof ApiError) return error;
  if (error instanceof DOMException && error.name === "AbortError") {
    return new ApiError(
      "timeout",
      "Request timed out",
      "The scan took too long to complete. Please try again.",
    );
  }
  return NETWORK_ERROR();
}
