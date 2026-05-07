/*
 * MEI Score Player — Pitch Processor AudioWorklet
 * Copyright (c) 2025 Alfred Leung
 * Licensed under the MIT License — see LICENSE
 *
 * Low-latency pitch detection via FFT.
 * Buffers incoming audio, applies a Hann window, computes the FFT,
 * finds the magnitude peak with parabolic interpolation, and posts
 * the detected frequency to the main thread.
 */

class PitchProcessor extends AudioWorkletProcessor {
  constructor() {
    super()
    this.sampleRate = sampleRate
    this.bufferSize = 2048
    this.buffer = new Float32Array(this.bufferSize)
    this.writePos = 0
    this.isReady = false
  }

  /** Hann window function */
  hann(x, N) {
    return 0.5 * (1 - Math.cos((2 * Math.PI * x) / (N - 1)))
  }

  /** Radix-2 in-place FFT */
  fft(buffer) {
    const N = buffer.length

    let j = 0
    for (let i = 1; i < N; i++) {
      let bit = N >> 1
      while (j & bit) { j ^= bit; bit >>= 1 }
      j ^= bit
      if (i < j) {
        [buffer[i], buffer[j]] = [buffer[j], buffer[i]]
      }
    }

    for (let len = 2; len <= N; len <<= 1) {
      const ang = -2 * Math.PI / len
      const wlenRe = Math.cos(ang)
      const wlenIm = Math.sin(ang)
      for (let i = 0; i < N; i += len) {
        let wRe = 1, wIm = 0
        for (let j = 0; j < len / 2; j++) {
          const uRe = buffer[i + j]
          const vRe = buffer[i + j + len/2] * wRe

          buffer[i + j] = uRe + vRe
          buffer[i + j + len/2] = uRe - vRe

          const nextWRe = wRe * wlenRe - wIm * wlenIm
          const nextWIm = wRe * wlenIm + wIm * wlenRe
          wRe = nextWRe; wIm = nextWIm
        }
      }
    }
  }

  /** Quadratic interpolation for sub-bin peak accuracy */
  parabolic(mag, idx) {
    if (idx <= 0 || idx >= mag.length - 1) return 0
    const alpha = mag[idx - 1]
    const beta  = mag[idx]
    const gamma = mag[idx + 1]
    return 0.5 * (alpha - gamma) / (alpha - 2*beta + gamma)
  }

  /** Process each audio block */
  process(inputs) {
    const input = inputs[0]
    if (input.length === 0) return true

    const channel = input[0]
    for (let i = 0; i < channel.length; i++) {
      this.buffer[this.writePos++] = channel[i]
      if (this.writePos >= this.bufferSize) {
        this.writePos = 0
        this.isReady = true
      }
    }

    if (this.isReady) {
      const buf = new Float32Array(this.bufferSize)
      for (let i = 0; i < this.bufferSize; i++) {
        buf[i] = this.buffer[(this.writePos + i) % this.bufferSize] * this.hann(i, this.bufferSize)
      }

      const fftBuf = new Float32Array(buf.length)
      fftBuf.set(buf)
      this.fft(fftBuf)

      const mag = new Float32Array(fftBuf.length / 2)
      for (let k = 0; k < mag.length; k++) {
        mag[k] = Math.abs(fftBuf[k])
      }

      let peakIdx = 0
      for (let k = 1; k < mag.length; k++) {
        if (mag[k] > mag[peakIdx]) peakIdx = k
      }

      const p = this.parabolic(mag, peakIdx)
      const freq = (peakIdx + p) * (this.sampleRate / this.bufferSize)

      this.port.postMessage({ freq })
    }

    return true
  }
}

registerProcessor('pitch-processor', PitchProcessor)
