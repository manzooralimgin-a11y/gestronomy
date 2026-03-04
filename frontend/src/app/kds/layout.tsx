export default function KDSLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-950 min-h-screen text-white">
        {children}
      </body>
    </html>
  );
}
