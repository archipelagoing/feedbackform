"use client";

import { Fragment, createElement, useMemo, type ReactNode } from "react";
import { fromMarkdown } from "mdast-util-from-markdown";
import { gfmFromMarkdown } from "mdast-util-gfm";
import { gfm } from "micromark-extension-gfm";

type Range = { start_utf16: number; end_utf16: number };
type MarkdownNode = {
  type: string; value?: string; children?: MarkdownNode[]; depth?: number;
  ordered?: boolean | null; start?: number | null; checked?: boolean | null;
  url?: string; identifier?: string; alt?: string | null;
  position?: { start: { offset?: number }; end: { offset?: number } };
};

export function markedSource(body: string, ranges: Range[], offset = 0): ReactNode {
  const merged: { start: number; end: number }[] = [];
  for (const range of [...ranges].sort((a, b) => a.start_utf16 - b.start_utf16)) {
    const start = Math.max(0, range.start_utf16 - offset);
    const end = Math.min(body.length, range.end_utf16 - offset);
    if (end <= start) continue;
    const last = merged.at(-1);
    if (last && start <= last.end) last.end = Math.max(last.end, end);
    else merged.push({ start, end });
  }
  const pieces: ReactNode[] = [];
  let cursor = 0;
  for (const range of merged) {
    pieces.push(body.slice(cursor, range.start));
    pieces.push(<mark key={range.start}>{body.slice(range.start, range.end)}</mark>);
    cursor = range.end;
  }
  pieces.push(body.slice(cursor));
  return pieces;
}

// Every mapped text leaf retains original UTF-16 offsets. DOM text length alone
// cannot locate a selection after Markdown syntax has been removed.
export function selectionSourceOffset(root: HTMLElement, node: Node, offset: number): number | null {
  const element = node.nodeType === Node.ELEMENT_NODE ? node as Element : node.parentElement;
  const leaf = element?.closest<HTMLElement>("[data-source-start]");
  if (!leaf || !root.contains(leaf)) return null;
  const prefix = document.createRange();
  prefix.selectNodeContents(leaf);
  prefix.setEnd(node, offset);
  const length = prefix.toString().length;
  return Number(leaf.dataset.sourceStart) + length;
}

function safeHref(value?: string): string | undefined {
  if (!value) return;
  try {
    const url = new URL(value);
    if (["https:", "http:", "mailto:"].includes(url.protocol)) return url.href;
  } catch { /* Unsupported or relative links remain readable text. */ }
}

export default function Markdown({ body, ranges = [], raw = false }: {
  body: string; ranges?: Range[]; raw?: boolean;
}) {
  const tree = useMemo(() => fromMarkdown(body, {
    extensions: [gfm()], mdastExtensions: [gfmFromMarkdown()],
  }), [body]);
  const definitions = new Map<string, string>();
  for (const node of tree.children) {
    if (node.type === "definition") definitions.set(node.identifier, node.url);
  }
  function literal(value: string, start?: number, end?: number): ReactNode {
    // Entity decoding, escapes and normalized code have no one-to-one mapping.
    // Keep them readable, and let the source view handle exact passage selection.
    if (start === undefined || end === undefined || body.slice(start, end) !== value) return value;
    return <span data-source-start={start}>{markedSource(value, ranges, start)}</span>;
  }
  function render(node: MarkdownNode, depth = 0): ReactNode {
    const start = node.position?.start.offset;
    const end = node.position?.end.offset;
    if (depth > 64) return body.slice(start, end);
    const children = node.children?.map((child, index) =>
      <Fragment key={index}>{render(child, depth + 1)}</Fragment>);
    switch (node.type) {
      case "root": return children;
      case "text": return literal(node.value ?? "", start, end);
      case "paragraph": return <p>{children}</p>;
      case "heading": return createElement(`h${Math.min(6, (node.depth ?? 1) + 2)}`, null, children);
      case "strong": return <strong>{children}</strong>;
      case "emphasis": return <em>{children}</em>;
      case "delete": return <del>{children}</del>;
      case "list": return node.ordered ? <ol start={node.start ?? 1}>{children}</ol> : <ul>{children}</ul>;
      case "listItem": return <li>{typeof node.checked === "boolean" &&
        <input type="checkbox" checked={node.checked} disabled aria-label="Task status" />}{children}</li>;
      case "blockquote": return <blockquote>{children}</blockquote>;
      case "inlineCode": return <code>{node.value}</code>;
      case "code": return <pre><code>{node.value}</code></pre>;
      case "break": return <br />;
      case "thematicBreak": return <hr />;
      case "link":
      case "linkReference": {
        const href = safeHref(node.url ?? definitions.get(node.identifier ?? ""));
        return href ? <a href={href} target="_blank" rel="noopener noreferrer">{children}</a> : children;
      }
      case "image":
      case "imageReference": return <span>[Image: {node.alt || "image"}]</span>;
      case "html": return literal(node.value ?? "", start, end);
      case "definition": return null;
      case "table": return <div className="markdown-table"><table>
        <thead>{node.children?.slice(0, 1).map((row, i) => <tr key={i}>
          {row.children?.map((cell, j) => <th key={j}>{render(cell, depth + 1)}</th>)}</tr>)}</thead>
        <tbody>{node.children?.slice(1).map((row, i) => <tr key={i}>
          {row.children?.map((cell, j) => <td key={j}>{render(cell, depth + 1)}</td>)}</tr>)}</tbody>
      </table></div>;
      case "tableCell": return children;
      default: return children ?? literal(body.slice(start, end), start, end);
    }
  }
  return raw ? <div className="markdown-source"><span data-source-start={0}>
    {markedSource(body, ranges)}</span></div>
    : <div className="markdown-body">{render(tree)}</div>;
}
