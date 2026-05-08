/*
 * MEI Score Player — Score Module
 * Copyright (c) 2025 Alfred Leung
 * Licensed under the MIT License — see LICENSE
 *
 * MIDI playback state machine, note rendering, page setup,
 * and MEI note-to-MIDI conversion utilities.
 */

import { audioCtx, piano } from './audio.js'

/** Playback states */
const PlayState = Object.freeze({
  STOPPED: 'stopped',
  PLAY: 'play',
  PAUSE: 'pause',
})

let currentState = PlayState.STOPPED

/** Get the current playback state */
export function getCurrentState() {
  return currentState
}

/**
 * Toggle play / pause / resume based on current state.
 * @param {string} midiString - data URL of the MIDI content
 */
export function playMIDI(midiString) {
  switch (currentState) {
  case PlayState.STOPPED:
    currentState = PlayState.PLAY
    MIDIjs.play(midiString)
    break

  case PlayState.PLAY:
    currentState = PlayState.PAUSE
    MIDIjs.pause()
    break

  case PlayState.PAUSE:
    currentState = PlayState.PLAY
    MIDIjs.resume()
    break

  default:
    break
  }
}

/** Stop playback and reset state */
export function stopMIDI() {
  MIDIjs.stop()
  currentState = PlayState.STOPPED
}

/** Play a single note with auto-stop after 800 ms */
export function playOneNote(note, velocity = 80) {
  if (!piano) return
  piano.play(note, audioCtx.currentTime, { velocity })
  setTimeout(() => piano.stop(), 800)
}

/** Send a Note-On event */
export function noteOn(note, velocity = 0.5) {
  if (!piano) return
  piano.play(note, audioCtx.currentTime, { velocity })
}

/** Send a Note-Off event */
export function noteOff() {
  if (!piano) return
  piano.stop()
}

/**
 * Play a single note with visual highlight.
 * @param {HTMLElement} svgNote - the SVG note element
 * @param {number} note - MIDI note number
 * @param {number} velocity
 */
function playSingleNote(svgNote, _track, note, velocity) {
  const fill = svgNote.getAttribute('fill')
  const color = svgNote.getAttribute('color')
  svgNote.setAttribute('fill', '#007f00')
  svgNote.setAttribute('color', '#007f00')
  noteOn(note, velocity)
  setTimeout(() => {
    svgNote.setAttribute('fill', fill)
    svgNote.setAttribute('color', color)
    noteOff()
  }, 1000)
}

/** Set MIDI playback tempo */
export function midiTempo(bpm) {
  if (typeof MIDIjs !== 'undefined') {
    MIDIjs.setTempo(bpm)
  }
}

/**
 * Convert MEI pitch attributes to a MIDI note number.
 * @param {string} pname - pitch class name (c, d, e, ...)
 * @param {number} octave - MEI octave number
 * @param {string} accid - accidental (s, ss, n, f, ff)
 */
export function midiNoteNumber(pname, octave, accid) {
  if (!pname || isNaN(octave)) return null
  const accidClass = { s: 1, ss: 2, n: 0, f: -1, ff: -2 }
  const pitchClass = { c: 0, d: 2, e: 4, f: 5, g: 7, a: 9, b: 11 }
  const pc = pitchClass[pname.toLowerCase()]
  const ac = accid ? accidClass[accid.toLowerCase()] : 0
  return 12 * (octave + 1) + pc + ac
}

/** Recursively resolve accidental from a MEI note element */
export function resolveAccidental(note) {
  let accid_tag = note.querySelector('accid')
  if (accid_tag) {
    return resolveAccidental(accid_tag)
  } else {
    accid_tag = note.getAttribute('accid')
    if (accid_tag) {
      return accid_tag
    }
    return note.getAttribute('accid.ges')
  }
}

/** Handle click on a note: look up pitch and play it */
function noteClicked(note, svgElements) {
  const id = note.getAttribute('id')
  const meiNote = svgElements.get(id)
  if (meiNote) {
    const accid = resolveAccidental(meiNote)
    let pitch = midiNoteNumber(
      meiNote.getAttribute('pname'),
      parseInt(meiNote.getAttribute('oct'), 10), accid)
    playSingleNote(note, 0, pitch, 80)
  }
}

/**
 * Parse the rendered SVG, map note IDs to MEI note elements.
 */
function parsePage(svg, meiNotes, svgElements) {
  const cleaned = svg.replace(/<\/?xsvg>/g, (match) => {
    return match.includes('/') ? '</svg>' : '<svg>'
  })
  const svgDoc = new DOMParser().parseFromString(cleaned, 'image/svg+xml')
  const allNotes = svgDoc.querySelectorAll('g.note')
  allNotes.forEach((note) => {
    const id = note.getAttribute('id')
    const meiNote = meiNotes.get(id)
    if (meiNote) {
      svgElements.set(id, meiNote)
    }
  })
}

/**
 * Set up a rendered page: attach click and hover handlers to all notes,
 * then parse the SVG to build the note lookup map.
 */
export function setupPage(svg, meiNotes, svgElements) {
  const docNotes = document.querySelectorAll('g.note')
  docNotes.forEach((note) => {
    note.addEventListener('click', () => {
      noteClicked(note, svgElements)
    })

    note.addEventListener('mouseenter', () => {
      highlightNote(note, true)
    })

    note.addEventListener('mouseleave', () => {
      highlightNote(note, false)
    })
  })
  parsePage(svg, meiNotes, svgElements)
}

/** Add or remove the hover-highlight class on a note element */
function highlightNote(noteEl, on) {
  if (on) {
    noteEl.classList.add('hover-highlight')
  } else {
    noteEl.classList.remove('hover-highlight')
  }
}

/** Generate a random base-36 hash ID */
export function genHashId() {
  const crypto = window.crypto || window.msCrypto
  const array = new Uint32Array(1)
  crypto.getRandomValues(array)

  return baseEncodeInt(array[0], 36)
}

const base62Chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

function baseEncodeInt(value, base) {
  if ((base < 10) || (base > 63)) {
    return 0
  }

  if (value < base) return base62Chars[value]
  let base62 = 0

  while (value) {
    base62 += base62Chars[value % base]
    value = Math.floor(value / base)
  }
  let reversed = [...base62].reverse().join('')

  return reversed
}
