
import { Check } from "lucide-react";
import { Button } from "@/components/ui/button";

const Benefits = () => {
  const benefitsList = [
    "Personalized user experiences based on AI analysis",
    "Smart automation of routine tasks",
    "Real-time data processing and insights",
    "Adaptive interfaces that learn user preferences",
    "Predictive features that anticipate user needs",
    "Enhanced productivity through intelligent assistants"
  ];

  return (
    <section id="benefits" className="py-20">
      <div className="container mx-auto px-4">
        <div className="flex flex-col lg:flex-row items-center">
          <div className="lg:w-1/2 mb-12 lg:mb-0 lg:pr-12">
            <div className="relative">
              <div className="absolute -z-10 top-0 left-0 w-72 h-72 bg-dnnr-teal/10 rounded-full filter blur-3xl"></div>
              <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
                <img
                  src="https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=800&q=80"
                  alt="Smart technology enhancing life"
                  className="w-full h-auto"
                />
              </div>
              <div className="absolute -bottom-6 -right-6 bg-dnnr-blue p-4 rounded-xl shadow-lg">
                <p className="text-white font-medium text-sm">
                  <span className="font-bold text-xl block mb-1">84%</span> 
                  improved user satisfaction
                </p>
              </div>
            </div>
          </div>
          
          <div className="lg:w-1/2">
            <h2 className="text-3xl md:text-4xl font-bold text-dnnr-blue mb-6">
              How Our AI Solutions <span className="text-dnnr-teal">Improve Lives</span>
            </h2>
            <p className="text-lg text-gray-700 mb-8">
              Our technology doesn't just make apps smarter—it makes daily life better. By combining cutting-edge AI with thoughtful design, we create solutions that truly understand and adapt to human needs.
            </p>
            
            <div className="mb-8">
              <ul className="space-y-4">
                {benefitsList.map((benefit, index) => (
                  <li key={index} className="flex items-start">
                    <span className="mr-3 mt-1 bg-dnnr-teal/20 p-1 rounded-full">
                      <Check size={16} className="text-dnnr-teal" />
                    </span>
                    <span className="text-gray-700">{benefit}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            <Button className="bg-dnnr-blue hover:bg-dnnr-blue-light">
              Learn How It Works
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Benefits;
