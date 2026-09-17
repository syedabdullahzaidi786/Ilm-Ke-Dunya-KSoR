import Link from "next/link";
import Image, { type StaticImageData } from "next/image";
import type { ReactElement } from "react";

import type { RecordEntry } from "@/lib/source";

export function HomeCover({
  foot,
  mark,
  name,
  title,
  purpose,
  documents,
  firstUrl,
  lead,
}: {
  mark: StaticImageData;
  name: string;
  title: string;
  purpose: string | null;
  documents: number;
  firstUrl: string;
  lead: RecordEntry;
  behind: readonly RecordEntry[];
  foot?: ReactElement;
}): ReactElement {
  const heroStats = [
    { label: "Core Services", value: "8" },
    { label: "Quran Surahs", value: "114" },
    { label: "Duas", value: "126" },
  ];

  const sections = [
    {
      eyebrow: "OpenAPI",
      title: "Ilm Ke Dunya OpenAPI",
      description:
        "A production-ready API layer for Quran, Hadith, Duas, Seerah, Qibla, Islamic names and more — designed for web apps, AI tools, and developer integrations.",
      action: "View OpenAPI",
      href: "https://ilm-ke-dunya-api.vercel.app",
      badge: "Live",
      accent: true,
      art: "api",
    },
    {
      eyebrow: "IDE integration",
      title: "IDEs Extension",
      description:
        "Bring trusted Islamic references directly into the tools developers and researchers already use — coming soon to IDE experiences and coding workflows.",
      action: "Coming soon",
      href: "#",
      badge: "Soon",
      accent: false,
      art: "ide",
    },
    {
      eyebrow: "Mobile access",
      title: "Mobile App",
      description:
        "A lightweight reading and reference app for daily Islamic learning, search, and quick access to trusted content — launching soon.",
      action: "Coming soon",
      href: "#",
      badge: "Soon",
      accent: false,
      art: "mobile",
    },
  ];

  const coverage = [
    {
      icon: "📖",
      title: "Quran",
      text: "Verses, translations, transliteration and structured surah metadata.",
    },
    {
      icon: "📕",
      title: "Hadith",
      text: "Collections, chapters, narration data, and authentic references.",
    },
    {
      icon: "🤲",
      title: "Duas",
      text: "Daily supplications, categories and source-backed guidance.",
    },
    {
      icon: "🕌",
      title: "Seerah",
      text: "Timeline, guidance and contextual Islamic learning resources.",
    },
  ];

  return (
    <section className="relative isolate flex min-h-[calc(100dvh-3.5rem)] flex-col overflow-hidden bg-[var(--ksor-cover)] text-[var(--ksor-cover-foreground)]">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(circle at top left, rgba(86,220,255,0.18), transparent 28%), radial-gradient(circle at bottom right, rgba(255,191,105,0.18), transparent 25%)",
        }}
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          backgroundImage:
            "linear-gradient(to right, rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.04) 1px, transparent 1px)",
          backgroundSize: "28px 28px",
          maskImage: "linear-gradient(to bottom, transparent, black 18%, black 82%, transparent)",
        }}
      />

      <div className="relative mx-auto w-full max-w-7xl px-6 py-10 lg:px-10 lg:py-14">
        <div className="mb-8 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-[var(--ksor-cover-rule)] bg-white/5">
              <Image src={mark} alt="" width={22} height={22} className="size-5 rounded-md" priority />
            </div>
            <div className="font-mono text-[10px] tracking-[0.22em] text-[var(--ksor-cover-muted)] uppercase">
              {name}
            </div>
          </div>
          <Link
            href={firstUrl}
            className="hidden rounded-full border border-[var(--ksor-cover-rule)] bg-white/5 px-4 py-2 font-mono text-[10px] tracking-[0.16em] text-[var(--ksor-cover-foreground)] uppercase transition-colors hover:border-[var(--primary)] hover:text-[var(--primary)] sm:inline-flex"
          >
            Explore library
          </Link>
        </div>

        <div className="grid items-center gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:gap-12">
          <div className="relative z-10">
            <p className="mb-4 font-mono text-[11px] tracking-[0.22em] text-[var(--primary)] uppercase">
              Trusted Islamic knowledge platform
            </p>
            <h1 className="max-w-3xl font-display text-[clamp(3rem,5vw,6rem)] leading-[0.9] font-semibold tracking-[-0.06em] text-balance">
              {title}
            </h1>

            {purpose === null ? null : (
              <p className="mt-6 max-w-xl text-base leading-8 text-[var(--ksor-cover-muted)] sm:text-lg">
                {purpose}
              </p>
            )}

            <div className="mt-8 flex flex-wrap items-center gap-3">
              <a
                href="https://ilm-ke-dunya-api.vercel.app/docs"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 rounded-xl bg-[var(--primary)] px-5 py-3.5 text-sm font-medium text-[var(--primary-foreground)] shadow-[0_12px_32px_rgba(117,211,255,0.28)] transition-all duration-200 hover:-translate-y-0.5"
              >
                Open API Docs
                <span aria-hidden>→</span>
              </a>
              <Link
                href={firstUrl}
                className="inline-flex items-center rounded-xl border border-[var(--ksor-cover-rule)] bg-white/4 px-5 py-3.5 text-sm font-medium text-[var(--ksor-cover-foreground)] transition-colors duration-200 hover:border-[var(--primary)] hover:text-[var(--primary)]"
              >
                Browse Knowledge
              </Link>
            </div>

            <div className="mt-8 grid max-w-xl grid-cols-3 gap-3">
              {heroStats.map((item) => (
                <div
                  key={item.label}
                  className="rounded-2xl border border-[var(--ksor-cover-rule)] bg-white/4 p-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]"
                >
                  <div className="font-mono text-[10px] tracking-[0.18em] text-[var(--ksor-cover-muted)] uppercase">
                    {item.label}
                  </div>
                  <div className="mt-2 font-display text-2xl font-semibold tracking-[-0.05em]">{item.value}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="relative z-10 flex justify-center lg:justify-end">
            <div className="relative w-full max-w-[30rem]">
              <div
                aria-hidden
                className="absolute -inset-6 rounded-[2.2rem] bg-[radial-gradient(circle,_rgba(117,211,255,0.28),_rgba(9,14,22,0)_65%)] blur-3xl"
              />

              <div className="relative rounded-[2rem] border border-[var(--ksor-cover-rule)] bg-[linear-gradient(180deg,rgba(17,24,39,0.95),rgba(11,16,27,0.92))] p-4 shadow-[0_28px_80px_rgba(8,12,20,0.6)]">
                <div className="rounded-[1.5rem] border border-white/10 bg-[linear-gradient(180deg,rgba(17,24,39,0.8),rgba(10,15,22,0.72))] p-4">
                  <div className="mb-4 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
                      <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
                      <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
                    </div>
                    <span className="font-mono text-[9px] tracking-[0.2em] text-[var(--ksor-cover-muted)] uppercase">
                      library
                    </span>
                  </div>

                  <div className="rounded-[1.3rem] border border-[var(--ksor-cover-rule)] bg-[linear-gradient(135deg,#fdf9ed,#e7f3ff_44%,#d6f0ff)] p-4 shadow-inner">
                    <div className="mb-4 flex items-center gap-3">
                      <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-slate-200 bg-white/80 shadow-sm">
                        <Image src={mark} alt="" width={24} height={24} className="size-6 rounded-lg" />
                      </div>
                      <div>
                        <div className="font-display text-2xl font-semibold tracking-[-0.06em] text-slate-900">
                          Ilm Ke Dunya
                        </div>
                        <div className="font-mono text-[9px] tracking-[0.18em] text-slate-500 uppercase">
                          knowledge platform
                        </div>
                      </div>
                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-white/70 p-3 text-left shadow-sm">
                      <div className="mb-2 flex items-center justify-between">
                        <span className="font-mono text-[9px] tracking-[0.2em] text-slate-500 uppercase">
                          {lead.title}
                        </span>
                        <span className="rounded-full bg-slate-900 px-2 py-1 font-mono text-[9px] text-white uppercase tracking-[0.12em]">
                          {documents} docs
                        </span>
                      </div>
                      <div className="space-y-2 text-sm text-slate-700">
                        <div className="h-2.5 w-full rounded-full bg-slate-200" />
                        <div className="h-2.5 w-4/5 rounded-full bg-slate-200" />
                        <div className="h-2.5 w-3/5 rounded-full bg-slate-200" />
                      </div>
                    </div>

                    <div className="mt-4 grid grid-cols-3 gap-2">
                      <div className="rounded-xl bg-slate-900 px-2 py-2 text-center text-[10px] font-medium tracking-[0.12em] text-white uppercase">
                        Quran
                      </div>
                      <div className="rounded-xl bg-sky-100 px-2 py-2 text-center text-[10px] font-medium tracking-[0.12em] text-sky-800 uppercase">
                        Hadith
                      </div>
                      <div className="rounded-xl bg-amber-100 px-2 py-2 text-center text-[10px] font-medium tracking-[0.12em] text-amber-800 uppercase">
                        Duas
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="relative mx-auto w-full max-w-6xl px-6 py-12 lg:px-8">
        {sections.map((section, index) => (
          <div
            key={section.title}
            className={`grid items-center gap-8 rounded-[2rem] border border-[var(--ksor-cover-rule)] bg-white/4 p-6 shadow-[0_20px_55px_-32px_rgba(10,20,32,0.8)] backdrop-blur-sm md:p-8 lg:grid-cols-2 ${
              index % 2 === 1 ? "mt-8" : "mt-0"
            }`}
          >
            <div className={index % 2 === 1 ? "lg:order-2" : ""}>
              <p className="font-mono text-[10px] tracking-[0.22em] text-[var(--primary)] uppercase">
                {section.eyebrow}
              </p>
              <h2 className="mt-3 font-display text-3xl font-semibold tracking-[-0.04em] text-[var(--ksor-cover-foreground)] sm:text-4xl">
                {section.title}
              </h2>
              <p className="mt-4 max-w-xl text-base leading-7 text-[var(--ksor-cover-muted)]">
                {section.description}
              </p>

              <div className="mt-6 flex items-center gap-3">
                {section.href === "#" ? (
                  <span className="inline-flex rounded-xl border border-[var(--ksor-cover-rule)] bg-transparent px-4 py-2.5 font-mono text-[10px] tracking-[0.18em] text-[var(--ksor-cover-muted)] uppercase">
                    {section.action}
                  </span>
                ) : (
                  <a
                    href={section.href}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex rounded-xl bg-[var(--primary)] px-4 py-2.5 font-mono text-[10px] tracking-[0.18em] text-[var(--primary-foreground)] uppercase transition-colors hover:brightness-110"
                  >
                    {section.action}
                  </a>
                )}
                <span className="rounded-full border border-[var(--ksor-cover-rule)] bg-white/5 px-2.5 py-1.5 font-mono text-[9px] tracking-[0.18em] text-[var(--ksor-cover-muted)] uppercase">
                  {section.badge}
                </span>
              </div>
            </div>

            <div className={index % 2 === 1 ? "lg:order-1" : ""}>
              <div
                className={`rounded-[1.8rem] border ${
                  section.accent
                    ? "border-[var(--primary)]/50 bg-[rgba(117,211,255,0.08)]"
                    : "border-[var(--ksor-cover-rule)] bg-white/3"
                } p-4 shadow-[0_18px_50px_-32px_rgba(15,23,42,0.9)]`}
              >
                {section.art === "api" ? (
                  <div className="rounded-[1.3rem] border border-white/10 bg-[linear-gradient(180deg,rgba(12,17,25,0.9),rgba(18,22,31,0.9))] p-4">
                    <div className="mb-3 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
                        <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
                        <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
                      </div>
                      <span className="font-mono text-[9px] tracking-[0.18em] text-slate-400 uppercase">
                        api
                      </span>
                    </div>
                    <div className="rounded-[1.1rem] border border-white/10 bg-slate-950/80 p-4">
                      <div className="mb-3 flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-700 bg-slate-900">
                          <Image src={mark} alt="" width={20} height={20} className="size-5 rounded-md" />
                        </div>
                        <div>
                          <div className="font-mono text-[9px] tracking-[0.2em] text-slate-400 uppercase">
                            GET /api/v1/quran
                          </div>
                          <div className="mt-1 font-display text-xl font-semibold tracking-[-0.05em] text-white">
                            OpenAPI
                          </div>
                        </div>
                      </div>
                      <div className="space-y-2 text-sm text-slate-300">
                        <div className="h-2.5 w-full rounded-full bg-slate-700" />
                        <div className="h-2.5 w-4/5 rounded-full bg-slate-700" />
                        <div className="h-2.5 w-2/3 rounded-full bg-slate-700" />
                        <div className="mt-4 flex gap-2">
                          <span className="rounded-full bg-sky-500/20 px-2 py-1 font-mono text-[9px] tracking-[0.18em] text-sky-300 uppercase">
                            json
                          </span>
                          <span className="rounded-full bg-emerald-500/20 px-2 py-1 font-mono text-[9px] tracking-[0.18em] text-emerald-300 uppercase">
                            public
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : null}

                {section.art === "ide" ? (
                  <div className="rounded-[1.3rem] border border-white/10 bg-[linear-gradient(180deg,#0b1220,#111c2c)] p-4">
                    <div className="grid gap-3 md:grid-cols-[0.8fr_1.2fr]">
                      <div className="rounded-2xl border border-white/10 bg-slate-900 p-3">
                        <div className="mb-2 h-2.5 w-2/3 rounded-full bg-slate-700" />
                        <div className="space-y-2">
                          <div className="h-2.5 rounded-full bg-slate-700" />
                          <div className="h-2.5 w-4/5 rounded-full bg-slate-700" />
                          <div className="h-2.5 w-3/5 rounded-full bg-slate-700" />
                        </div>
                      </div>
                      <div className="rounded-2xl border border-[var(--primary)]/40 bg-[rgba(117,211,255,0.08)] p-4">
                        <div className="font-mono text-[9px] tracking-[0.2em] text-[var(--primary)] uppercase">
                          extension preview
                        </div>
                        <div className="mt-3 font-display text-2xl font-semibold tracking-[-0.05em] text-white">
                          AI-ready tools
                        </div>
                        <div className="mt-2 text-sm leading-6 text-slate-300">
                          Search, fetch and integrate Islamic knowledge directly in developer workflows.
                        </div>
                      </div>
                    </div>
                  </div>
                ) : null}

                {section.art === "mobile" ? (
                  <div className="rounded-[1.3rem] border border-white/10 bg-[linear-gradient(180deg,#0f172a,#111827)] p-4">
                    <div className="mx-auto max-w-[220px] rounded-[2rem] border border-white/10 bg-[linear-gradient(180deg,#111827,#090d14)] p-3 shadow-[0_16px_40px_rgba(0,0,0,0.5)]">
                      <div className="mb-3 flex justify-center">
                        <div className="h-1.5 w-12 rounded-full bg-slate-700" />
                      </div>
                      <div className="rounded-[1.4rem] border border-white/10 bg-[linear-gradient(180deg,#eaf7ff,#dfeaf5)] p-3 text-slate-900">
                        <div className="mb-3 flex items-center gap-2">
                          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white shadow-sm">
                            <Image src={mark} alt="" width={18} height={18} className="size-4 rounded-md" />
                          </div>
                          <div>
                            <div className="font-display text-lg font-semibold tracking-[-0.04em]">Ilm Ke Dunya</div>
                            <div className="font-mono text-[8px] tracking-[0.16em] text-slate-500 uppercase">mobile app</div>
                          </div>
                        </div>
                        <div className="space-y-2">
                          <div className="h-2.5 w-full rounded-full bg-slate-200" />
                          <div className="h-2.5 w-4/5 rounded-full bg-slate-200" />
                          <div className="h-2.5 w-2/3 rounded-full bg-slate-200" />
                        </div>
                      </div>
                    </div>
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="relative mx-auto w-full max-w-6xl px-6 pb-16 lg:px-8">
        <div className="mb-6">
          <p className="font-mono text-[10px] tracking-[0.2em] text-[var(--primary)] uppercase">
            Coverage
          </p>
          <h2 className="mt-3 font-display text-3xl font-semibold tracking-[-0.04em] text-[var(--ksor-cover-foreground)] sm:text-4xl">
            What it covers
          </h2>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {coverage.map((item) => (
            <div
              key={item.title}
              className="rounded-[1.5rem] border border-[var(--ksor-cover-rule)] bg-white/4 p-5 transition-transform duration-200 hover:-translate-y-1 hover:border-[var(--primary)]/60"
            >
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl border border-[var(--ksor-cover-rule)] bg-[rgba(117,211,255,0.08)] text-xl">
                {item.icon}
              </div>
              <h3 className="font-display text-2xl font-semibold tracking-[-0.04em] text-[var(--ksor-cover-foreground)]">
                {item.title}
              </h3>
              <p className="mt-3 text-sm leading-6 text-[var(--ksor-cover-muted)]">{item.text}</p>
            </div>
          ))}
        </div>
      </div>

      {foot === undefined ? null : <div className="relative mx-auto w-full max-w-6xl px-6 pb-8 lg:px-8">{foot}</div>}
    </section>
  );
}
