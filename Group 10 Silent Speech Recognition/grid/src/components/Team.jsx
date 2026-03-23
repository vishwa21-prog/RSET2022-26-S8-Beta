import React from 'react'

const teamCards = [
  {
    name: 'Darsan Prasad',
    role: 'ML Engineer',
    front: 'Builds models that decode silent speech.',
    back: 'Specializes in deep learning & inference.',
    highlight: 'Optimized real-time prediction pipeline.'
  },
  {
    name: 'Fathima Meharin Irshad',
    role: 'UI/UX Designer',
    front: 'Designs clean, accessible interfaces.',
    back: 'Focuses on user flow and visual clarity.',
    highlight: 'Led usability testing and layout design.'
  },
  {
    name: 'Geevar Saji Kuriakose',
    role: 'ML Engineer',
    front: 'Trains models on diverse visual datasets.',
    back: 'Works on cross-user generalization.',
    highlight: 'Curated multi-modal training data.'
  },
  {
    name: 'Giribala Arun',
    role: 'Frontend Engineer',
    front: 'Implements responsive, polished UIs.',
    back: 'Expert in React and Tailwind CSS.',
    highlight: 'Built adaptive website components with responsiveness.'
  }
]

const Team = () => {
  return (
    <section id="team" className="w-full py-20 px-6 md:px-8">
      <div className="max-w-screen-lg mx-auto flex flex-col items-center text-center gap-6">
        <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold text-[#64dfdf] tracking-tight leading-tight">
          Meet the Team
        </h1>
        <p className="text-base md:text-xl text-[#56cfe1] max-w-4xl leading-relaxed">
          SilentSpeech is built by a focused team of engineers and designers. From decoding silent signals to crafting seamless interfaces, each member brings precision and purpose to the project.
        </p>
      </div>

      {/* Flippable Cards Section */}
      <div className="max-w-screen-lg mx-auto mt-16 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
        {teamCards.map((member, index) => (
          <div key={index} className="group perspective">
            <div className="relative w-full h-64 transition-transform duration-700 transform-style-preserve-3d group-hover:rotate-y-180">
              {/* Front Side */}
              <div className="absolute w-full h-full bg-[#000000] text-[#56cfe1] border border-gray-200 rounded-xl shadow-md p-6 flex flex-col justify-center items-center backface-hidden">
                <h3 className="text-xl font-semibold text-primary mb-1">{member.name}</h3>
                <p className="text-[1.1rem] text-gray-400 mb-2">{member.role}</p>
                <p className="text-[1rem] text-gray-400 text-center">{member.front}</p>
              </div>
              {/* Back Side */}
              <div className="absolute w-full h-full bg-black text-[#56cfe1] rounded-xl shadow-md p-6 flex flex-col justify-center items-center rotate-y-180 backface-hidden">
                <p className="text-[1.2rem] text-[#56cfe1] text-center mb-2">{member.back}</p>
                <p className="text-[1rem] text-gray-400 text-center">Key: {member.highlight}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

export default Team