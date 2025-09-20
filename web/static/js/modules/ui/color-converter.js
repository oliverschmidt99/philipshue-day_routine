// Konvertiert CIE XY-Farbwerte in RGB
export function xyToRgb(x, y, brightness = 1.0) {
  const Y = brightness;
  const X = (Y / y) * x;
  const Z = (Y / y) * (1 - x - y);

  let r = X * 3.2406 - Y * 1.5372 - Z * 0.4986;
  let g = -X * 0.9689 + Y * 1.8758 + Z * 0.0415;
  let b = X * 0.0557 - Y * 0.204 + Z * 1.057;

  r =
    r <= 0.0031308 ? 12.92 * r : (1.0 + 0.055) * Math.pow(r, 1.0 / 2.4) - 0.055;
  g =
    g <= 0.0031308 ? 12.92 * g : (1.0 + 0.055) * Math.pow(g, 1.0 / 2.4) - 0.055;
  b =
    b <= 0.0031308 ? 12.92 * b : (1.0 + 0.055) * Math.pow(b, 1.0 / 2.4) - 0.055;

  return {
    r: Math.round(Math.max(0, Math.min(255, r * 255))),
    g: Math.round(Math.max(0, Math.min(255, g * 255))),
    b: Math.round(Math.max(0, Math.min(255, b * 255))),
  };
}

// Konvertiert Farbtemperatur in Mired zu RGB
export function mirekToRgb(mirek) {
  const kelvin = 1000000 / mirek;
  const temp = kelvin / 100;
  let r, g, b;

  if (temp <= 66) {
    r = 255;
    g = 99.4708025861 * Math.log(temp) - 161.1195681661;
  } else {
    r = 329.698727446 * Math.pow(temp - 60, -0.1332047592);
    g = 288.1221695283 * Math.pow(temp - 60, -0.0755148492);
  }

  if (temp >= 66) {
    b = 255;
  } else if (temp <= 19) {
    b = 0;
  } else {
    b = 138.5177312231 * Math.log(temp - 10) - 305.0447927307;
  }

  return {
    r: Math.round(Math.max(0, Math.min(255, r))),
    g: Math.round(Math.max(0, Math.min(255, g))),
    b: Math.round(Math.max(0, Math.min(255, b))),
  };
}

// Hilfsfunktion für lesbare Textfarbe
export function getContrastYIQ(rgb) {
  const yiq = (rgb.r * 299 + rgb.g * 587 + rgb.b * 114) / 1000;
  return yiq >= 128 ? "black" : "white";
}
