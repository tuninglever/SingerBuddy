/*
 * MEI Score Player — Audio Module
 * Copyright (c) 2025 Alfred Leung
 * Licensed under the MIT License — see LICENSE
 *
 * Manages AudioContext, pitch detection, and soundfont loading.
 * Provides frequency-to-MIDI conversion and peak detection.
 */

export let audioCtx, pitchCtx
export let piano, choir
let pitchTracking = false
let pitchStream, pitchSource
export let spectrumAnalyser

let bufferLen

/** Convert a MIDI note number to a human-readable name (e.g. "C4") */
export function midiToNoteName(midi) {
  const notes = ['C', 'C#', 'D', 'D#', 'E', 'F',
                  'F#', 'G', 'G#', 'A', 'A#', 'B']

  const octave = Math.floor(midi / 12) - 1
  const noteName = notes[midi % 12]

  return `${noteName}${octave}`
}

/** Convert a frequency (Hz) to the nearest MIDI note number */
export function freqToMidi(f) {
  return Math.round(69 + 12 * Math.log2(f / 440))
}

/** Load piano and choir instruments from the soundfont library */
async function loadLocalSF() {
  piano = await Soundfont.instrument(audioCtx, 'acoustic_grand_piano')
  choir = await Soundfont.instrument(audioCtx, 'choir_aahs')
}

/** Initialize audio contexts, analyser, and pitch-detection worklet */
export function initAudio(stream) {
  audioCtx = new (window.AudioContext || window.webkitAudioContext)()

  pitchStream = stream
  pitchCtx = new (window.AudioContext || window.webkitAudioContext)()
  pitchSource = pitchCtx.createMediaStreamSource(stream)

  spectrumAnalyser = pitchCtx.createAnalyser()
  spectrumAnalyser.fftSize = 4096
  spectrumAnalyser.smoothingTimeConstant = 0.8
  pitchSource.connect(spectrumAnalyser)
  bufferLen = spectrumAnalyser.frequencyBinCount

  pitchCtx.audioWorklet.addModule('scripts/pitch-processor.js')
    .then(() => {
      const pitchNode = new AudioWorkletNode(pitchCtx, 'pitch-processor')
      pitchSource.connect(pitchNode)
    })
  loadLocalSF()
}

/** Enable pitch tracking */
export function pitchTrackingOn() {
  pitchTracking = true
}

/** Disable pitch tracking */
export function pitchTrackingOff() {
  pitchTracking = false
}

/** Return current pitch-tracking state */
export function isPitchTracking() {
  return pitchTracking
}

/** Stop pitch detection and release microphone tracks */
export function stopPitchDetection() {
  pitchTracking = false

  if (pitchStream) {
    pitchStream.getTracks().forEach(track => track.stop())
  }
}

/**
 * Analyse the frequency spectrum from an AnalyserNode.
 * Finds local maxima, applies parabolic interpolation for sub-bin accuracy,
 * and returns the dominant frequency, MIDI note, and note name.
 */
export function estimateAudio(analyser) {
  const bufferLength = analyser.frequencyBinCount
  const dataArray = new Uint8Array(bufferLength)

  analyser.getByteFrequencyData(dataArray)

  /* Find all local maxima */
  const peaks = []
  for (let i = 1; i < bufferLen - 1; i++) {
    const left  = dataArray[i - 1]
    const curr  = dataArray[i]
    const right = dataArray[i + 1]

    if (curr > left && curr > right) {
      peaks.push({ index: i, amp: curr })
    }
  }

  /* Filter peaks by amplitude threshold */
  const ampThreshold = (Math.max(...dataArray) - Math.min(...dataArray)) * 0.7
  const filteredPeaks = peaks.filter(p => p.amp >= ampThreshold)

  /* Map peaks to frequencies with parabolic interpolation, sorted ascending */
  const freqPeaks = filteredPeaks
        .map(p => {
          const left  = p.index > 0 ? dataArray[p.index - 1] : 0
          const right = p.index < bufferLen - 1 ? dataArray[p.index + 1] : 0
          const delta = (right - left) / (2 * (2 * p.amp - right - left))
          const bin   = p.index + delta

          const freq = (bin * audioCtx.sampleRate) / analyser.fftSize
          return { freq, amp: p.amp }
        })
        .sort((a, b) => a.freq - b.freq)

  /* Pick the dominant (lowest-frequency) peak */
  const dom = freqPeaks[0] || { freq: 0, amp: 0 }
  const midi = dom.freq > 0 ? freqToMidi(dom.freq) : '--'
  const note = `${midiToNoteName(midi)}`

  return { freq: dom.freq, midi, note }
}
