/*
 * MEI Score Player
 * Copyright (c) 2025 Alfred Leung
 * Licensed under the MIT License — see LICENSE
 *
 * Main application entry point:
 *   - File loading (.mei only)
 *   - Playback controls (play/pause/stop)
 *   - Page navigation
 *   - Verovio initialization and score rendering
 *   - MIDI highlighting callback
 *   - Pitch tracking and spectrum controls
 */

import { initAudio, pitchTrackingOn, pitchTrackingOff, isPitchTracking, estimateAudio, spectrumAnalyser } from './audio.js'
import { playMIDI, stopMIDI, setupPage, genHashId } from './score.js'
import { listMicrophones, startSpectrum, stopSpectrum } from './spectrum.js'
import { voiceMap, volumeChangedSet, volumeChangedGet, meiDoc } from './state.js'

/* ---------- Global state ---------- */
let tk = null
let svgElements = new Map()
let meiNotes = new Map()
let currentPage = 1
let pageCount = 0

const fileInput = document.getElementById('fileInput')
const pickBtn   = document.getElementById('pickBtn')
const pitchBtn  = document.getElementById('pitchBtn')

let doDraw = false
let pitchDrawId = 0

/* ---------- File I/O ---------- */

function readFileAsText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload  = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsText(file)
  })
}

pickBtn.addEventListener('click', () => fileInput.click())
fileInput.addEventListener('change', async (e) => {
  const file = e.target.files[0]
  if (!file) return

  if (!file.name.toLowerCase().endsWith('.mei')) {
    console.error('Only .mei files are supported')
    fileInput.value = ''
    return
  }

  try {
    const meiTxt = await readFileAsText(file)

    if (!tk) {
      console.error('Verovio not initialized')
      fileInput.value = ''
      return
    }

    meiNotes.clear()
    svgElements.clear()

    const doc = new DOMParser().parseFromString(meiTxt, 'application/xml')
    const notes = doc.querySelectorAll('note')
    notes.forEach((note) => {
      const id = note.getAttribute('xml:id')
      if (id) meiNotes.set(id, note)
    })

    setupVoiceVolumes(doc)
    loadAndRender()
    pageCount = tk.getPageCount()
  } catch (err) {
    console.error(`Error reading file: ${err.message}`)
  }

  fileInput.value = ''
})

/* ---------- Tempo slider ---------- */

const tempoSlider   = document.getElementById('tempoSlider')
const tempoValue    = document.getElementById('tempoValue')

tempoValue.textContent = tempoSlider.value
tempoSlider.addEventListener('input', () => {
  let value = parseInt(tempoSlider.value, 10)
  tk.setOptions({
    midiTempoAdjustment: parseInt(value, 10) / 120.0
  })
  tempoValue.textContent = tempoSlider.value
})

/* ---------- Menu toggle ---------- */

const toggleMenuBtn = document.getElementById('toggleMenu')
const menuPanel = document.getElementById('menuPanel')
const voiceVolumes = document.getElementById('voiceVolumes')

if (toggleMenuBtn && menuPanel) {
  toggleMenuBtn.addEventListener('click', () => {
    const isVisible =
          (menuPanel.style.display !== 'none' && menuPanel.style.display !== '')

    if (isVisible) {
      menuPanel.style.display = 'none'
    } else {
      menuPanel.style.display = 'block'
    }
  })
}

const closeMenuBtn = document.getElementById('closeMenu')
if (closeMenuBtn && menuPanel) {
  closeMenuBtn.addEventListener('click', () => {
    menuPanel.style.display = 'none'
  })
}

/* ---------- Voice volume UI setup ---------- */

function setupVoiceVolumes(doc) {
  meiDoc.meiDoc = doc
  voiceMap.clear()
  voiceVolumes.innerHTML = ''

  const staffDefs = doc.querySelectorAll('staffDef')
  staffDefs.forEach((staff) => {
    const label = staff.querySelector('label')
    let instrDef = staff.querySelector('instrDef')
    let name
    if (label) {
      name = label.textContent
      voiceVolumes.innerHTML +=
        `<label for="${name}" class="voiceVol">${name}:</label>
         <input class="voiceRange" type="range" id="${name}_Slider" min="1" max="127" step="1" value="127">`
      let sliderName = `${name}_Slider`
      voiceMap.set(staff.getAttribute('xml:id'), sliderName)
    }
    if (!instrDef) {
      let iid = genHashId()
      instrDef = staff.ownerDocument.createElement('instrDef')
      instrDef.setAttribute('xml:id', iid)
      instrDef.setAttribute('midi.volume', '100%')
      if (label) {
        const voiceLabels = ['Soprano', 'Alto', 'Tenor', 'Baritone', 'Bass']
        if (voiceLabels.includes(label.textContent)) {
          instrDef.setAttribute('midi.instrnum', '52')
        }
      }
      staff.appendChild(instrDef)
    }
  })

  voiceMap.forEach((slider) => {
    let volumeSlider = document.getElementById(slider)
    if (volumeSlider) {
      volumeSlider.addEventListener('click', () => {
        volumeChangedSet(true)
      })
      volumeSlider.addEventListener('change', () => {
        volumeChangedSet(true)
      })
    }
  })
}

function loadAndRender() {
  let finalXML = (new XMLSerializer()).serializeToString(meiDoc.meiDoc)
  tk.loadData(finalXML)
  currentPage = 1
  let svg = tk.renderToSVG(currentPage)
  document.getElementById('notation').innerHTML = svg
  setupPage(svg, meiNotes, svgElements)
  volumeChangedSet(false)
}

function applyVolumeChanges() {
  if (!volumeChangedGet()) return

  const mei = meiDoc.meiDoc
  if (!mei) return

  const staffDefs = mei.querySelectorAll('staffDef')
  staffDefs.forEach((staff) => {
    const staffId = staff.getAttribute('xml:id')
    const sliderId = voiceMap.get(staffId)
    if (!sliderId) return

    const slider = document.getElementById(sliderId)
    const value = slider ? slider.value : 127
    const percent = Math.round((value / 127) * 100)

    let instrDef = staff.querySelector('instrDef')
    if (!instrDef) {
      instrDef = mei.createElement('instrDef')
      instrDef.setAttribute('xml:id', genHashId())
      const label = staff.querySelector('label')
      if (label) {
        const voiceLabels = ['Soprano', 'Alto', 'Tenor', 'Baritone', 'Bass']
        if (voiceLabels.includes(label.textContent)) {
          instrDef.setAttribute('midi.instrnum', '52')
        }
      }
      staff.appendChild(instrDef)
    }
    instrDef.setAttribute('midi.volume', `${percent}%`)
  })

  const finalXML = new XMLSerializer().serializeToString(mei)
  tk.loadData(finalXML)
  volumeChangedSet(false)
}

/* ---------- Initialization ---------- */

document.addEventListener('DOMContentLoaded', () => {
  const constraints = { audio: true, video: false }
  navigator.mediaDevices.getUserMedia(constraints)
    .then(stream => initAudio(stream))
    .catch(err => {
      console.error('Microphone error:', err)
    })

  verovio.module.onRuntimeInitialized = function () {
    tk = new verovio.toolkit()

    /* MIDI playback highlighting callback */
    const midiHighlightingHandler = function (event) {
      let playingNotes = document.querySelectorAll('g.note.playing')
      for (let playingNote of playingNotes) playingNote.classList.remove('playing')

      let currentElements = tk.getElementsAtTime(event.time * 1000)

      if (!currentElements || currentElements.page < 1) return

      if (currentElements.page !== currentPage) {
        currentPage = currentElements.page
        let svg = tk.renderToSVG(currentPage)
        document.getElementById('notation').innerHTML = svg
        setupPage(svg, meiNotes, svgElements)
      }

      if (currentElements.notes && currentElements.notes.length) {
        for (let noteId of currentElements.notes) {
          let noteElement = document.getElementById(noteId)
          if (noteElement) {
            noteElement.classList.add('playing')
          }
        }
      }
    }

    /* Page navigation */
    const nextPage = function () {
      if (currentPage < pageCount) {
        currentPage += 1
        let svg = tk.renderToSVG(currentPage)
        document.getElementById('notation').innerHTML = svg
        setupPage(svg, meiNotes, svgElements)
      }
    }
    const prevPage = function () {
      if (currentPage > 1) {
        currentPage -= 1
        let svg = tk.renderToSVG(currentPage)
        document.getElementById('notation').innerHTML = svg
        setupPage(svg, meiNotes, svgElements)
      }
    }

    /* Wire up toolbar buttons */
    document.getElementById('playMIDI').addEventListener(
      'click', () => {
        applyVolumeChanges()
        let base64midi = tk.renderToMIDI()
        let midiString = 'data:audio/midi;base64,' + base64midi
        playMIDI(midiString)
      })
    document.getElementById('stopMIDI').addEventListener('click', stopMIDI)
    document.getElementById('nextPage').addEventListener('click', nextPage)
    document.getElementById('prevPage').addEventListener('click', prevPage)

    MIDIjs.player_callback = midiHighlightingHandler

    /* Load default score */
    fetch('scores/Tallis_O_Lord.mei')
      .then((response) => response.text())
      .then((meiXML) => {
        tk.setOptions({
          pageWidth: document.body.clientWidth,
          scaleToPageSize: true,
          scale: 40,
          breaks: false,
          landscape: false,
          breaks: 'encoded'
        })

        const doc = new DOMParser().parseFromString(meiXML, 'application/xml')
        const notes = doc.querySelectorAll('note')
        notes.forEach((note) => {
          const id = note.getAttribute('xml:id')
          if (id) meiNotes.set(id, note)
        })

        setupVoiceVolumes(doc)
        loadAndRender()

        pageCount = tk.getPageCount()
      })

    /* Pitch tracking toggle */
    pitchBtn.addEventListener('click', () => {
      if (!isPitchTracking()) {
        pitchTrackingOn()
        const domFreq = document.getElementById('domFreq')
        const domMidi = document.getElementById('domMidi')
        const domNote = document.getElementById('domNote')

        function trackPitch() {
          pitchDrawId = requestAnimationFrame(trackPitch)
          const result = estimateAudio(spectrumAnalyser)
          domFreq.textContent = `${result.freq.toFixed(1)} Hz`
          domMidi.textContent = `MIDI ${result.midi}`

          const expectedFreq = 440 * Math.pow(2, (result.midi - 69) / 12)
          const cents = 1200 * Math.log2(result.freq / expectedFreq)
          const threshold = 25

          domFreq.className = 'pitch-info'
          domMidi.className = 'pitch-info'
          domNote.className = 'pitch-info'
          pitchBtn.classList.remove('pitch-sharp', 'pitch-flat', 'pitch-in')

          if (Math.abs(cents) < threshold) {
            domNote.textContent = result.note
            domFreq.classList.add('pitch-in')
            domMidi.classList.add('pitch-in')
            domNote.classList.add('pitch-in')
            pitchBtn.classList.add('pitch-in')
          } else if (cents > 0) {
            domNote.textContent = `${result.note} ↑`
            domFreq.classList.add('pitch-sharp')
            domMidi.classList.add('pitch-sharp')
            domNote.classList.add('pitch-sharp')
            pitchBtn.classList.add('pitch-sharp')
          } else {
            domNote.textContent = `${result.note} ↓`
            domFreq.classList.add('pitch-flat')
            domMidi.classList.add('pitch-flat')
            domNote.classList.add('pitch-flat')
            pitchBtn.classList.add('pitch-flat')
          }
        }
        trackPitch()
      } else {
        pitchTrackingOff()
        cancelAnimationFrame(pitchDrawId)
        pitchDrawId = 0
        domFreq.textContent = ''
        domMidi.textContent = ''
        domNote.textContent = ''
        domFreq.className = 'pitch-info'
        domMidi.className = 'pitch-info'
        domNote.className = 'pitch-info'
        pitchBtn.classList.remove('pitch-sharp', 'pitch-flat', 'pitch-in')
      }
    })

    /* Spectrum analyzer toggle */
    const startBtn = document.getElementById('spectrumStart')
    startBtn.addEventListener('click', () => {
      if (false == doDraw) {
        startSpectrum()
        startBtn.textContent = 'Stop'
        doDraw = true
      } else {
        stopSpectrum()
        doDraw = false
        startBtn.textContent = 'Start'
      }
    })

    listMicrophones()

    navigator.mediaDevices.addEventListener('devicechange', () => {
      listMicrophones()
    })
  }
})
