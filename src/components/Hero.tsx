
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

const Hero = () => {
  return (
    <section className="relative bg-hero-pattern py-20 md:py-28">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row items-center">
          <div className="md:w-1/2 mb-12 md:mb-0">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-dnnr-blue mb-6">
              AI-Powered Solutions for{" "}
              <span className="text-dnnr-teal">Smarter Living</span>
            </h1>
            <p className="text-lg text-gray-700 mb-8 max-w-lg">
              We build intelligent web and mobile applications that transform everyday experiences through personalized AI features.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Button className="bg-dnnr-teal hover:bg-dnnr-teal/90 text-white px-6 py-6">
                Get Started
              </Button>
              <Button variant="outline" className="border-dnnr-blue text-dnnr-blue hover:bg-dnnr-blue/10 px-6 py-6">
                Learn More <ArrowRight size={16} className="ml-2" />
              </Button>
            </div>
          </div>
          <div className="md:w-1/2 flex justify-center">
            <div className="relative w-full max-w-md">
              <div className="absolute -top-4 -left-4 w-72 h-72 bg-dnnr-blue/10 rounded-full filter blur-2xl"></div>
              <div className="absolute -bottom-8 -right-8 w-72 h-72 bg-dnnr-teal/10 rounded-full filter blur-2xl"></div>
              <div className="relative bg-white p-4 rounded-2xl shadow-lg animate-float">
                <img
                  src="https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80"
                  alt="AI-powered mobile app interface"
                  className="w-full h-auto rounded-xl"
                />
                <div className="absolute -bottom-4 -right-4 bg-white p-2 rounded-full shadow-lg">
                  <div className="bg-dnnr-teal w-12 h-12 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-lg">AI</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
