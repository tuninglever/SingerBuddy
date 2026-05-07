/*
 * MEI Score Player — Spectrum Module
 * Copyright (c) 2025 Alfred Leung
 * Licensed under the MIT License — see LICENSE
 *
 * Spectrum analyzer visualization and microphone enumeration.
 */

import {
  spectrumAnalyser, estimateAudio
} from './audio.js'

/** List all available audio input devices and populate the selector */
export async function listMicrophones() {
  const devices = await navigator.mediaDevices.enumerateDevices()
  const micSelect = document.getElementById('micSelect')
  micSelect.innerHTML = ''

  const select = document.createElement('select')
  devices
    .filter(d => d.kind === 'audioinput')
    .forEach((d, i) => {
      const opt = document.createElement('option')
      opt.value = d.deviceId
      opt.textContent = d.label || `Microphone ${i + 1}`
      select.appendChild(opt)
    })
  micSelect.appendChild(select)
}

let drawId = 0

/** Cancel the spectrum draw loop */
export async function stopSpectrum() {
  cancelAnimationFrame(drawId)
  drawId = 0
}

/**
 * Start the spectrum analyzer: draw frequency bars on the canvas
 * and update the dominant frequency / note readout each frame.
 */
export async function startSpectrum() {
  const canvas = document.getElementById('spectrumCanvas')
  const ctx2d = canvas.getContext('2d')

  function resizeCanvas() {
    const dpr = window.devicePixelRatio || 1
    canvas.width  = canvas.clientWidth * dpr
    canvas.height = canvas.clientHeight * dpr
    ctx2d.scale(dpr, dpr)
  }
  window.addEventListener('resize', resizeCanvas)
  resizeCanvas()

  const bufferLength = spectrumAnalyser.frequencyBinCount
  const dataArray   = new Uint8Array(bufferLength)

  const specFreq  = document.getElementById('specFreq')
  const specMidi  = document.getElementById('specMidi')
  const specNote  = document.getElementById('specNote')

  function draw() {
    drawId = requestAnimationFrame(draw)
    spectrumAnalyser.getByteFrequencyData(dataArray)

    ctx2d.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight)

    const barWidth = (canvas.clientWidth) / bufferLength
    let x = 0

    for (let i = 0; i < bufferLength; i++) {
      const barHeight = dataArray[i] / 255 * canvas.clientHeight

      const hue = i / bufferLength * 360
      ctx2d.fillStyle = `hsl(${hue}, 100%, 50%)`

      ctx2d.fillRect(x, canvas.clientHeight - barHeight, barWidth, barHeight)
      x += barWidth + 1
    }

    const result = estimateAudio(spectrumAnalyser)
    specFreq.textContent = `${result.freq.toFixed(1)}`
    specMidi.textContent = ` -- ${result.midi}`
    specNote.textContent = ` -- ${result.note}`
  }

  draw()
}
