/*
 * MEI Score Player — Shared State
 * Copyright (c) 2025 Alfred Leung
 * Licensed under the MIT License — see LICENSE
 *
 * Central store for application-wide state:
 *   - voiceMap: maps staff IDs to volume slider element IDs
 *   - volumeChanged: flag raised when a voice slider is adjusted
 */

export const voiceMap = new Map()
export let volumeChanged = false
export const meiDoc = { meiDoc: null }

export function volumeChangedGet() {
  return volumeChanged === true
}

export function volumeChangedSet(state) {
  volumeChanged = state
}
