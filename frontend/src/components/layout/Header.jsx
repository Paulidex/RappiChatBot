import text from "../../constants/text.json";

export default function Header() {
  return (
    <header className="col-span-1 rounded-xl bg-white p-3 sm:p-4 gap-4 sm:gap-6 md:gap-8 shadow-md flex flex-row items-center w-full box-border">
      <div className="w-12 sm:w-16 md:w-20 shrink-0 px-2 sm:px-3 py-2 rounded-2xl bg-linear-to-t from-[#ff3e53] to-[#fd6331]">
        <img src="/mostacho.png" alt={text.header.logoAlt} className="w-full h-auto" />
      </div>
      <h1 className="font-bold text-xl sm:text-2xl md:text-3xl lg:text-4xl truncate">
        {text.header.title}
      </h1>
    </header>
  );
}
