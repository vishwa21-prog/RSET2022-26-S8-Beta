import React from 'react'

const About = () => {
  return (
    <div className="max-w-screen-lg mx-auto px-6 md:px-8 py-16 flex flex-col justify-center items-center text-center gap-6 z-10">
        <h1 className="text-3xl md:text-5xl font-bold animate-fadeIn text-[#64dfdf]">
          About Us
        </h1>
        <p className="text-base md:text-xl text-[#56cfe1] max-w-4xl leading-relaxed">
          We believe communication is a fundamental human right. Our mission is to empower individuals who cannot speak by providing cutting-edge silent speech recognition technology. Through innovation, empathy, and collaboration, we aim to bridge the gap between thought and expression—giving voice to the voiceless.
        </p>
        <p className="text-base md:text-xl text-[#56cfe1] max-w-4xl leading-relaxed">
          Our team brings together researchers, engineers, and designers dedicated to accessibility and inclusion. We’re proud to represent <span className="font-semibold">Rajagiri School of Engineering & Technology</span> in this transformative journey, building tools that make a real difference in people’s lives.
        </p>
    </div>
  )
}

export default About