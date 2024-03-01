"use client";

import { on } from "events";
import Image from "next/image";
import Link from "next/link";
import React, { useState } from "react";

export default function Home() {
  const [data, setData] = useState("");
  const [prompt, setPrompt] = useState(
    "Type your prompt here and click the button to generate a response."
  );
  console.log(prompt)

  const callApi = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/python", {
        method: "POST",
        body: JSON.stringify({ prompt }),
        headers: { "Content-Type": "application/json" },
      });
      const data = await response.json();
      console.log("🚀 ~ callApi ~ data:", data);
      setData(data.message);
    } catch (error) {
      console.error("There was an error accessing the API", error);
      setData("Failed to fetch data.");
    }
  };

  return (
    <main className="w-full flex min-h-screen flex-col items-center justify-between">
      <nav className="flex items-center justify-between w-full px-6 py-4 bg-gradient-to-r from-blue-500 to-teal-400">
        <h1 className=" text-centerfont-bold">TEST APP</h1>
      </nav>
      <div className="w-full p-10">
        {" "}
        <textarea
          className="w-full"
          name="prompt"
          id="2"
          cols={30}
          rows={10}
          value={prompt}
          onClick={() => setPrompt("")}
          onChange={(e) => setPrompt(e.target.value)}
        ></textarea>
      </div>

      <div className=" w-full p-10">
        <textarea
          className="w-full"
          name="textarea"
          id="1"
          cols={30}
          rows={10}
          value={data}
          readOnly
        ></textarea>
      </div>

      <button
        onClick={callApi}
        className=" p-4 border border-black bg-cyan-500 rounded-md flex items-center justify-center text-white font-semibold text-sm hover:bg-cyan-600 transition duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
      >
        {" "}
        click me{" "}
      </button>
    </main>
  );
}
