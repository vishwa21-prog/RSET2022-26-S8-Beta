import React from 'react'

const techCards = [
  {
    title: 'Visual Recognition',
    front: 'Analyzes lip movements and facial expressions.',
    back: 'Uses computer vision to decode silent articulation.',
    svgPath: '/assets/visual-recognition.svg'
  },
  {
    title: 'Deep Learning',
    front: 'Learns silent speech patterns across users.',
    back: 'Trained on diverse visual datasets.',
    svgPath: '/assets/deep-learning.svg'
  },
  {
    title: 'Real-Time Inference',
    front: 'Processes input instantly for seamless interaction.',
    back: 'Delivers low-latency predictions.',
    svgPath: '/assets/real-time.svg'
  }
]

const Technology = () => {
  return (
    <section id="technology" className="w-full py-20 px-6 md:px-8">
      <div className="max-w-screen-lg mx-auto flex flex-col items-center text-center gap-6">
        <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold text-[#64dfdf] tracking-tight leading-tight">
          Technology Used
        </h1>
        <p className="text-base md:text-xl text-[#56cfe1] max-w-4xl leading-relaxed">
          Our silent speech recognition system combines advanced signal processing, machine learning, and sensor integration to decode unspoken communication. By capturing subtle facial movements, muscle signals, and gestures, our technology translates silent intent into spoken language—instantly and accurately.
        </p>
        <p className="text-base md:text-xl text-[#56cfe1] max-w-4xl leading-relaxed">
          Built with accessibility and real-world usability in mind, our platform is lightweight, responsive, and adaptable to diverse user needs. Whether it's wearable sensors or camera-based input, SilentSpeech is designed to empower expression without sound.
        </p>
      </div>

      {/* Flippable Cards Section */}
      <div className="max-w-screen-lg mx-auto mt-16 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
        {techCards.map((card, index) => (
          <div key={index} className="group perspective">
            <div className="relative w-full h-64 transition-transform duration-700 transform-style-preserve-3d group-hover:rotate-y-180">
              {/* Front Side */}
              <div className="absolute w-full h-full bg-[#000000] text-[#56cfe1] border border-gray-200 rounded-xl shadow-md p-6 flex flex-col justify-center items-center backface-hidden">
                <img src={card.svgPath} alt={card.title} className="h-12 w-12 mb-4" />
                <h3 className="text-xl font-semibold text-primary mb-2">{card.title}</h3>
                <p className="text-[1.1rem] text-gray-400 text-center">{card.front}</p>
              </div>
              {/* Back Side */}
              <div className="absolute w-full h-full bg-black text-[#56cfe1] rounded-xl shadow-md p-6 flex flex-col justify-center items-center rotate-y-180 backface-hidden">
                <p className="text-[1.2rem] text-[#56cfe1] text-center mb-4">{card.back}</p>
                <ul className="list-disc list-inside text-[1rem] text-gray-400 text-left max-w-xs space-y-1">
                  {card.title === 'Visual Recognition' && (
                    <>
                      <li>Tracks lip contours and motion </li>
                      <li>Facial landmark detection</li>
                      <li>Gesture-based input mapping</li>
                    </>
                  )}
                  {card.title === 'Deep Learning' && (
                    <>
                      <li>Multi-modal training datasets</li>
                      <li>Adaptive model tuning</li>
                      <li>Cross-user generalization</li>
                    </>
                  )}
                  {card.title === 'Real-Time Inference' && (
                    <>
                      <li>Latency under 100ms</li>
                      <li>Edge-device optimization</li>
                      <li>Seamless API integration</li>
                    </>
                  )}
                </ul>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

export default Technology