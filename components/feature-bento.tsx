"use client";

import React from "react";
import {
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Image,
  Button,
} from "@nextui-org/react";

export default function FeaturesBento() {
  return (
    <div className="max-w-[900px] gap-4 grid grid-cols-12 grid-rows-2 px-8 mt-20">
      {/* Browser Automation Card */}
      <Card className="col-span-12 sm:col-span-4 h-[300px]">
        <CardHeader className="absolute z-10 top-1 flex-col !items-start bg-black/40 backdrop-blur-sm rounded-lg m-2 p-3">
          <p className="text-tiny text-white/80 uppercase font-bold">
            Automation
          </p>
          <h4 className="text-white font-medium text-large">
            Browser Automation Agent
          </h4>
        </CardHeader>
        <Image
          removeWrapper
          alt="Browser automation background"
          className="z-0 w-full h-full object-cover"
          src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop&crop=center"
        />
      </Card>

      {/* Tools Integration Card */}
      <Card className="col-span-12 sm:col-span-4 h-[300px]">
        <CardHeader className="absolute z-10 top-1 flex-col !items-start bg-black/40 backdrop-blur-sm rounded-lg m-2 p-3">
          <p className="text-tiny text-white/80 uppercase font-bold">
            Connected
          </p>
          <h4 className="text-white font-medium text-large">
            Tools Integration Hub
          </h4>
        </CardHeader>
        <Image
          removeWrapper
          alt="Tools integration background"
          className="z-0 w-full h-full object-cover"
          src="https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=300&fit=crop&crop=center"
        />
      </Card>

      {/* LLM Support Card */}
      <Card className="col-span-12 sm:col-span-4 h-[300px]">
        <CardHeader className="absolute z-10 top-1 flex-col !items-start bg-black/40 backdrop-blur-sm rounded-lg m-2 p-3">
          <p className="text-tiny text-white/80 uppercase font-bold">
            Intelligent
          </p>
          <h4 className="text-white font-medium text-large">
            Advanced LLM Support
          </h4>
        </CardHeader>
        <Image
          removeWrapper
          alt="LLM support background"
          className="z-0 w-full h-full object-cover"
          src="https://images.unsplash.com/photo-1676299081847-824916de030a?w=400&h=300&fit=crop&crop=center"
        />
      </Card>

      {/* New Agentic AI Card */}
      <Card isFooterBlurred className="w-full h-[300px] col-span-12">
        <CardHeader className="absolute z-10 top-4 left-4 flex-col items-start">
          <p className="text-tiny text-white/80 uppercase font-bold tracking-wider">
            Next Generation
          </p>
          <h4 className="text-white font-bold text-2xl">
            Agentic AI Revolution
          </h4>
          <p className="text-white/70 text-sm mt-2 max-w-md">
            Experience the future of autonomous AI agents that think, learn, and
            act independently to solve complex problems
          </p>
        </CardHeader>
        <Image
          removeWrapper
          alt="Agentic AI background"
          className="z-0 w-full h-full object-cover"
          src="https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=400&fit=crop&crop=center"
        />
        <CardFooter className="absolute bg-gradient-to-t from-black/80 via-black/40 to-transparent bottom-0 z-10 border-t-1 border-white/20">
          <div className="flex flex-grow gap-3 items-center">
            <div className="w-12 h-12 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-center">
              <span className="text-white font-bold text-lg">AI</span>
            </div>
            <div className="flex flex-col">
              <p className="text-sm text-white font-medium">
                Autonomous Intelligence
              </p>
              <p className="text-xs text-white/70">
                Self-directed AI agents working 24/7
              </p>
            </div>
          </div>
          <Button
            className="bg-gradient-to-r from-purple-500 to-blue-500 text-white font-semibold"
            radius="full"
            size="sm"
          >
            Explore AI
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
