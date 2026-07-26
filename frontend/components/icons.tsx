type IconProps = { className?: string };

const base = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.6,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

export function IconDashboard({ className }: IconProps) {
  return (
    <svg {...base} className={className}>
      <rect x="3.5" y="3.5" width="7" height="7" rx="1.4" />
      <rect x="13.5" y="3.5" width="7" height="7" rx="1.4" />
      <rect x="3.5" y="13.5" width="7" height="7" rx="1.4" />
      <rect x="13.5" y="13.5" width="7" height="7" rx="1.4" />
    </svg>
  );
}

export function IconCadastro({ className }: IconProps) {
  return (
    <svg {...base} className={className}>
      <ellipse cx="12" cy="5.5" rx="7.5" ry="2.5" />
      <path d="M4.5 5.5v13c0 1.38 3.36 2.5 7.5 2.5s7.5-1.12 7.5-2.5v-13" />
      <path d="M4.5 12c0 1.38 3.36 2.5 7.5 2.5s7.5-1.12 7.5-2.5" />
    </svg>
  );
}

export function IconEstoque({ className }: IconProps) {
  return (
    <svg {...base} className={className}>
      <path d="M12 3 20.5 7.5 12 12 3.5 7.5 12 3Z" />
      <path d="M3.5 7.5v9L12 21l8.5-4.5v-9" />
      <path d="M12 12v9" />
    </svg>
  );
}

export function IconMotor({ className }: IconProps) {
  return (
    <svg {...base} className={className}>
      <path d="M4.5 9a7.5 7.5 0 0 1 13-4.9" />
      <path d="M17 2.7v3.6h-3.6" />
      <path d="M19.5 15a7.5 7.5 0 0 1-13 4.9" />
      <path d="M7 21.3v-3.6h3.6" />
    </svg>
  );
}

export function IconOtimizacao({ className }: IconProps) {
  return (
    <svg {...base} className={className}>
      <circle cx="5" cy="18" r="2.2" />
      <circle cx="19" cy="6" r="2.2" />
      <circle cx="17" cy="18" r="2.2" />
      <path d="M7 17 17 7" />
      <path d="M7 18.5h7.8" />
    </svg>
  );
}

export function IconRelatorios({ className }: IconProps) {
  return (
    <svg {...base} className={className}>
      <path d="M4 21V10" />
      <path d="M12 21V4" />
      <path d="M20 21v-7" />
      <path d="M3 21h18" />
    </svg>
  );
}

export function IconConfig({ className }: IconProps) {
  return (
    <svg {...base} className={className}>
      <path d="M3.5 6h9" />
      <circle cx="15.5" cy="6" r="2" />
      <path d="M20.5 18h-9" />
      <circle cx="8.5" cy="18" r="2" />
      <path d="M3.5 12h13" />
      <circle cx="19" cy="12" r="2" />
    </svg>
  );
}
