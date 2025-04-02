
import { CircleUserRound, Brain, Sparkles, TrendingUp } from "lucide-react";

const Technology = () => {
  return (
    <section id="technology" className="py-20 bg-gradient-to-b from-gray-50 to-white">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-dnnr-blue mb-4">
            Our <span className="text-dnnr-teal">Technology</span>
          </h2>
          <p className="text-lg text-gray-700 max-w-2xl mx-auto">
            We leverage cutting-edge AI to create applications that understand, adapt, and evolve with your users.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 max-w-5xl mx-auto">
          <div className="flex flex-col items-center text-center md:items-start md:text-left">
            <div className="bg-dnnr-blue/10 p-4 rounded-2xl mb-6">
              <CircleUserRound size={32} className="text-dnnr-blue" />
            </div>
            <h3 className="text-xl font-bold text-dnnr-blue mb-3">Personalized User Experiences</h3>
            <p className="text-gray-700">
              Our AI analyzes user behavior to create truly personalized experiences that adapt to individual preferences and needs.
            </p>
          </div>
          
          <div className="flex flex-col items-center text-center md:items-start md:text-left">
            <div className="bg-dnnr-teal/10 p-4 rounded-2xl mb-6">
              <Brain size={32} className="text-dnnr-teal" />
            </div>
            <h3 className="text-xl font-bold text-dnnr-teal mb-3">Machine Learning Integration</h3>
            <p className="text-gray-700">
              We integrate sophisticated machine learning models that continuously improve based on user interactions and feedback.
            </p>
          </div>
          
          <div className="flex flex-col items-center text-center md:items-start md:text-left">
            <div className="bg-dnnr-teal/10 p-4 rounded-2xl mb-6">
              <Sparkles size={32} className="text-dnnr-teal" />
            </div>
            <h3 className="text-xl font-bold text-dnnr-teal mb-3">Smart Automation</h3>
            <p className="text-gray-700">
              Automate routine tasks and processes with AI that understands context and makes intelligent decisions.
            </p>
          </div>
          
          <div className="flex flex-col items-center text-center md:items-start md:text-left">
            <div className="bg-dnnr-blue/10 p-4 rounded-2xl mb-6">
              <TrendingUp size={32} className="text-dnnr-blue" />
            </div>
            <h3 className="text-xl font-bold text-dnnr-blue mb-3">Predictive Analytics</h3>
            <p className="text-gray-700">
              Leverage predictive algorithms that anticipate user needs and provide proactive solutions before issues arise.
            </p>
          </div>
        </div>
        
        <div className="mt-20 bg-tech-gradient p-8 md:p-12 rounded-2xl text-white text-center">
          <h3 className="text-2xl md:text-3xl font-bold mb-4">Ready to transform your digital experience?</h3>
          <p className="text-lg mb-8 max-w-2xl mx-auto">
            Join the companies already using our AI-powered solutions to create exceptional user experiences.
          </p>
          <div className="flex flex-wrap justify-center gap-8 md:gap-16">
            <div className="font-bold text-2xl opacity-80">CompanyOne</div>
            <div className="font-bold text-2xl opacity-80">BrandTwo</div>
            <div className="font-bold text-2xl opacity-80">TechFirm</div>
            <div className="font-bold text-2xl opacity-80">StartupX</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Technology;
