import os
import glob
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import zipfile

def extract_value(pattern, content, default=""):
    match = re.search(pattern, content)
    return match.group(1) if match else default

def parse_curve_data(data_string):
    values = data_string.split(',')
    return ' '.join([val.strip() for val in values])

def lrtemplate_to_xmp(lrtemplate_data):
    xmpmeta = ET.Element("x:xmpmeta", {
        "xmlns:x": "adobe:ns:meta/",
        "xmlns:rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    })
    rdf = ET.SubElement(xmpmeta, "rdf:RDF")
    description = ET.SubElement(rdf, "rdf:Description")
    description.set("xmlns:crs", "http://ns.adobe.com/camera-raw-settings/1.0/")
    
    # Извлекаем значения
	
    settings = {
        "WhiteBalance": extract_value(r'WhiteBalance\s*=\s*"([^"]+)"', lrtemplate_data, "As Shot"),
        "Sharpness": extract_value(r'Sharpness\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "25"),
        "ColorNoiseReduction": extract_value(r'ColorNoiseReduction\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "25"),
        "ConvertToGrayscale": extract_value(r'ConvertToGrayscale\s*=\s*([\w]+)', lrtemplate_data, "true"),
        "ProcessVersion": extract_value(r'ProcessVersion\s*=\s*"([\d.]+)"', lrtemplate_data, "10.0"),
        "CameraProfile": extract_value(r'CameraProfile\s*=\s*"([^"]+)"', lrtemplate_data, "Adobe Standard"),
        "ToneCurveName2012": extract_value(r'ToneCurveName2012\s*=\s*"([^"]+)"', lrtemplate_data, "Custom"),
        "Exposure2012": extract_value(r'Exposure2012\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "0"),
        "Contrast2012": extract_value(r'Contrast2012\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "0"),
        "Highlights2012": extract_value(r'Highlights2012\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "-2"),
        "Shadows2012": extract_value(r'Shadows2012\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "-2"),
        "Whites2012": extract_value(r'Whites2012\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "-10"),
        "Blacks2012": extract_value(r'Blacks2012\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "-10"),
        "Clarity2012": extract_value(r'Clarity2012\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "+10"),
        "Dehaze": extract_value(r'Dehaze\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "0"),
        "AutoLateralCA": extract_value(r'AutoLateralCA\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "0"),
        "BlueHue": extract_value(r'BlueHue\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "0"),
        "BlueSaturation": extract_value(r'BlueSaturation\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "0"),
        "ChromaticAberrationB": extract_value(r'ChromaticAberrationB\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "0"),
        "ChromaticAberrationR": extract_value(r'ChromaticAberrationR\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "0"),
        "GreenHue": extract_value(r'GreenHue\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "0"),
        "GreenSaturation": extract_value(r'GreenSaturation\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "0"),
        "RedHue": extract_value(r'RedHue\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "0"),
        "RedSaturation": extract_value(r'RedSaturation\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "0"),
        "ShadowTint": extract_value(r'ShadowTint\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "0"),
        "VignetteAmount": extract_value(r'VignetteAmount\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data, "0"),
        "EnableCalibration": extract_value(r'EnableCalibration\s*=\s*([\w]+)', lrtemplate_data, "true"),
        "EnableColorAdjustments": extract_value(r'EnableColorAdjustments\s*=\s*([\w]+)', lrtemplate_data, "true"),
        "EnableDetail": extract_value(r'EnableDetail\s*=\s*([\w]+)', lrtemplate_data, "true"),
        "EnableEffects": extract_value(r'EnableEffects\s*=\s*([\w]+)', lrtemplate_data, "true"),
        "EnableSplitToning": extract_value(r'EnableSplitToning\s*=\s*([\w]+)', lrtemplate_data, "true"),
        "Saturation": extract_value(r'\bSaturation\b\s*=\s*(-?\d+)', lrtemplate_data),
        "HueAdjustmentRed": extract_value(r'HueAdjustmentRed\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "HueAdjustmentOrange": extract_value(r'HueAdjustmentOrange\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "HueAdjustmentYellow": extract_value(r'HueAdjustmentYellow\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),  
        "HueAdjustmentGreen": extract_value(r'HueAdjustmentGreen\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "HueAdjustmentAqua": extract_value(r'HueAdjustmentAqua\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "HueAdjustmentBlue": extract_value(r'HueAdjustmentBlue\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "HueAdjustmentPurple": extract_value(r'HueAdjustmentPurple\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "HueAdjustmentMagenta": extract_value(r'HueAdjustmentMagenta\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "SaturationAdjustmentRed": extract_value(r'SaturationAdjustmentRed\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "SaturationAdjustmentOrange": extract_value(r'SaturationAdjustmentOrange\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "SaturationAdjustmentYellow": extract_value(r'SaturationAdjustmentYellow\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "SaturationAdjustmentGreen": extract_value(r'SaturationAdjustmentGreen\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "SaturationAdjustmentAqua": extract_value(r'SaturationAdjustmentAqua\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "SaturationAdjustmentBlue": extract_value(r'SaturationAdjustmentBlue\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "SaturationAdjustmentPurple": extract_value(r'SaturationAdjustmentPurple\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "SaturationAdjustmentMagenta": extract_value(r'SaturationAdjustmentMagenta\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "LuminanceAdjustmentRed": extract_value(r'LuminanceAdjustmentRed\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "LuminanceAdjustmentOrange": extract_value(r'LuminanceAdjustmentOrange\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "LuminanceAdjustmentYellow": extract_value(r'LuminanceAdjustmentYellow\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "LuminanceAdjustmentGreen": extract_value(r'LuminanceAdjustmentGreen\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "LuminanceAdjustmentAqua": extract_value(r'LuminanceAdjustmentAqua\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "LuminanceAdjustmentBlue": extract_value(r'LuminanceAdjustmentBlue\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "LuminanceAdjustmentPurple": extract_value(r'LuminanceAdjustmentPurple\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "LuminanceAdjustmentMagenta": extract_value(r'LuminanceAdjustmentMagenta\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "ToneCurvePV2012": parse_curve_data(extract_value(r'ToneCurvePV2012\s*=\s*\{([^\}]+)\}', lrtemplate_data)), 
        "ToneCurvePV2012Red": parse_curve_data(extract_value(r'ToneCurvePV2012Red\s*=\s*\{([^\}]+)\}', lrtemplate_data)),
        "ToneCurvePV2012Green": parse_curve_data(extract_value(r'ToneCurvePV2012Green\s*=\s*\{([^\}]+)\}', lrtemplate_data)),
        "ToneCurvePV2012Blue": parse_curve_data(extract_value(r'ToneCurvePV2012Blue\s*=\s*\{([^\}]+)\}', lrtemplate_data)),
        "PostCropVignetteFeather": extract_value(r'PostCropVignetteFeather\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "PostCropVignetteMidpoint": extract_value(r'PostCropVignetteMidpoint\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "PostCropVignetteRoundness": extract_value(r'PostCropVignetteRoundness\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "PostCropVignetteStyle": extract_value(r'PostCropVignetteStyle\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "SharpenDetail": extract_value(r'SharpenDetail\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "SharpenEdgeMasking": extract_value(r'SharpenEdgeMasking\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "SharpenRadius": extract_value(r'SharpenRadius\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "GrainAmount": extract_value(r'GrainAmount\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "GrainFrequency": extract_value(r'GrainFrequency\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "GrainSize": extract_value(r'GrainSize\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "SplitToningBalance": extract_value(r'SplitToningBalance\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "SplitToningHighlightHue": extract_value(r'SplitToningHighlightHue\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "SplitToningHighlightSaturation": extract_value(r'SplitToningHighlightSaturation\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "SplitToningShadowHue": extract_value(r'SplitToningShadowHue\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "SplitToningShadowSaturation": extract_value(r'SplitToningShadowSaturation\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "IncrementalTemperature": extract_value(r'IncrementalTemperature\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "IncrementalTint": extract_value(r'IncrementalTint\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "LuminanceNoiseReductionContrast": extract_value(r'LuminanceNoiseReductionContrast\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "LuminanceNoiseReductionDetail": extract_value(r'LuminanceNoiseReductionDetail\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "ColorNoiseReductionDetail": extract_value(r'ColorNoiseReductionDetail\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "ColorNoiseReductionSmoothness": extract_value(r'ColorNoiseReductionSmoothness\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "ParametricDarks": extract_value(r'ParametricDarks\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "ParametricLights": extract_value(r'ParametricLights\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "ParametricShadowSplit": extract_value(r'ParametricShadowSplit\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "ParametricMidtoneSplit": extract_value(r'ParametricMidtoneSplit\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
        "ParametricHighlightSplit": extract_value(r'ParametricHighlightSplit\s*=\s*([-]?\d+(?:\.\d+)?)', lrtemplate_data),
		"Vibrance": extract_value(r'\bVibrance\b\s*=\s*(-?\d+)', lrtemplate_data),        
    }

    for key, value in settings.items():
        ET.SubElement(description, f"crs:{key}").text = value

    # Преобразование в строку и форматирование
    xml_string = ET.tostring(xmpmeta, encoding="unicode")
    xml_pretty = minidom.parseString(xml_string).toprettyxml(indent="  ")

    return xml_pretty

def zip_file(filename):
    zip_filename = filename + ".zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        zipf.write(filename)
    # Удаляем оригинальный файл после архивации (если это нужно)
    # os.remove(filename)

def main():
    for filepath in glob.glob("*.lrtemplate"):
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            xmp_content = lrtemplate_to_xmp(content)
            xmp_filepath = os.path.splitext(filepath)[0] + ".xmp"
            with open(xmp_filepath, 'w', encoding='utf-8') as xmp_file:
                xmp_file.write(xmp_content)
            zip_file(xmp_filepath)  # Архивируем XMP файл	

if __name__ == "__main__":
    main()