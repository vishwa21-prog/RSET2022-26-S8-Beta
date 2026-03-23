import React from 'react'

const steps = [
  {
    title: 'Input Capture',
    description: 'Facial movements and lip contours are recorded via camera or sensor array.'
  },
  {
    title: 'Feature Extraction',
    description: 'Landmark detection and motion tracking isolate key visual features.'
  },
  {
    title: 'Model Inference',
    description: 'Deep learning models decode silent articulation into phonetic representations.'
  },
  {
    title: 'Real-Time Output',
    description: 'Predictions are rendered instantly as text or speech with minimal latency.'
  }
]

const Implementation = () => {
  return (
    <section id="implementation" className="w-full py-20 px-6 md:px-8">
      <div className="max-w-screen-lg mx-auto flex flex-col items-center text-center gap-6">
        <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold text-[#64dfdf] tracking-tight leading-tight">
          Real-Time Implementation
        </h1>
        <p className="text-base md:text-xl text-[#56cfe1] max-w-4xl leading-relaxed">
          Our system processes visual speech cues through a carefully designed, streamlined pipeline, where each step is thoughtfully optimized to ensure speed, clarity, and precision. From the moment visual input is received, every stage—from data preprocessing to feature extraction and final interpretation—is fine-tuned to deliver accurate results in real time. This approach not only enhances performance but also ensures a smooth and responsive experience for users who rely on clear, intuitive communication.
        </p>
      </div>

      {/* 2-column Circle Layout */}
      <div className="max-w-screen-md mx-auto mt-20 grid grid-cols-1 md:grid-cols-2 gap-16">
        {steps.map((step, index) => (
          <div key={index} className="flex flex-col items-center text-center">
            <div className="w-16 h-16 rounded-full bg-[#64dfdf] flex items-center justify-center text-black font-bold text-lg mb-6">
              {index + 1}
            </div>
            <h3 className="text-xl font-semibold text-[#64dfdf] mb-2">{step.title}</h3>
            <p className="text-[1rem] text-gray-400 max-w-xs">{step.description}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

export default Implementation