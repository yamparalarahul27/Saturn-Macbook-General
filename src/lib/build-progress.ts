"use client";

import { useMemo, useSyncExternalStore } from "react";

import { ship, steps } from "@/lib/ship";

const KEY = `paper-craft:vikramaditya:${ship.version}`;
const CHANGE = "paper-craft:progress";
const EMPTY = '{"step":0,"completed":[]}';
let fallback = EMPTY;
type Progress = { step: number; completed: number[] };
function read() {
  try {
    return localStorage.getItem(KEY) ?? fallback;
  } catch {
    return fallback;
  }
}
function parse(value: string): Progress {
  try {
    const data = JSON.parse(value);
    return {
      step: Number.isInteger(data.step)
        ? Math.max(0, Math.min(steps.length - 1, data.step))
        : 0,
      completed: Array.isArray(data.completed)
        ? [
            ...new Set<number>(
              data.completed.filter(
                (n: unknown) =>
                  typeof n === "number" &&
                  Number.isInteger(n) &&
                  n >= 0 &&
                  n < steps.length,
              ),
            ),
          ]
        : [],
    };
  } catch {
    return { step: 0, completed: [] };
  }
}
function subscribe(onChange: () => void) {
  window.addEventListener("storage", onChange);
  window.addEventListener(CHANGE, onChange);
  return () => {
    window.removeEventListener("storage", onChange);
    window.removeEventListener(CHANGE, onChange);
  };
}
export function useBuildProgress() {
  const snapshot = useSyncExternalStore(subscribe, read, () => EMPTY);
  const progress = useMemo(() => parse(snapshot), [snapshot]);
  function update(patch: Partial<Progress>) {
    fallback = JSON.stringify({ ...parse(read()), ...patch });
    try {
      localStorage.setItem(KEY, fallback);
    } catch {
      /* Session progress still works when storage is unavailable. */
    }
    window.dispatchEvent(new Event(CHANGE));
  }
  return { ...progress, update };
}
