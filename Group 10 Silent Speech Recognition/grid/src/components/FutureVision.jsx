import React from "react"

const futureCards = [
  {
    title: "Multilingual Visual Recognition",
    front: "Expand lip-reading models to support multiple languages and dialects.",
    back: "Inclusive communication across cultures and regions.",
    highlight: "Language Diversity",
  },
  {
    title: "AR/VR Integration",
    front: "Integrate silent speech into immersive AR/VR environments.",
    back: "Enhancing accessibility in virtual worlds.",
    highlight: "Immersive Tech",
  },
  {
    title: "Wearable Devices",
    front: "Design discreet wearables for natural facial cue capture.",
    back: "Seamless daily use with minimal intrusion.",
    highlight: "On-the-Go UX",
  },
  {
    title: "Cross-User Adaptation",
    front: "Generalize models across diverse facial features.",
    back: "Robust performance for all users.",
    highlight: "Model Flexibility",
  },
]

const FutureVision = () => {
  return (
    <section id="future" className="relative w-full py-20 px-6 md:px-8 bg-black">
      {/* Heading */}
      <div className="relative max-w-screen-lg mx-auto flex flex-col items-center text-center gap-6 z-10">
        <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold text-[#64dfdf] tracking-tight leading-tight">
          Future Vision
        </h1>
        <p className="text-base md:text-xl text-[#56cfe1] max-w-4xl leading-relaxed">
          SilentSpeech is evolving toward a world where visual communication becomes effortless,
          accurate, and universal. Our roadmap focuses on making visual speech recognition more
          adaptive, inclusive, and practical for real-world use.
        </p>
      </div>

      {/* Card Section */}
      <div className="max-w-screen-lg mx-auto mt-16 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
        {futureCards.map((card, index) => (
          <div key={index} className="group perspective">
            <div className="relative w-full h-64 transition-transform duration-700 transform-style-preserve-3d group-hover:rotate-y-180">
              {/* Front Side */}
              <div className="absolute w-full h-full bg-[#000000] text-[#56cfe1] border border-gray-200 rounded-xl shadow-md p-6 flex flex-col justify-center items-center backface-hidden">
                <h3 className="text-xl font-semibold text-primary mb-2 text-center">{card.title}</h3>
                <p className="text-[1rem] text-gray-400 text-center">{card.front}</p>
              </div>
              {/* Back Side */}
              <div className="absolute w-full h-full bg-black text-[#56cfe1] rounded-xl shadow-md p-6 flex flex-col justify-center items-center rotate-y-180 backface-hidden">
                <p className="text-[1.2rem] text-[#56cfe1] text-center mb-2">{card.back}</p>
                <p className="text-[1rem] text-gray-400 text-center">Key: {card.highlight}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

export default FutureVision