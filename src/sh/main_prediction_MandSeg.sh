#!/bin/sh

Help()
{
# Display Help
echo "Program to train and evaluate a 2D U-Net segmentation model"
echo
echo "Syntax: main_prediction.sh [--options]"
echo "options:"
echo "--dir_src                 Folder containing the scripts."
echo "--dir_input               Folder containing the scans to segment."
echo "--dir_output              Folder to save the postprocessed images"
echo "--width                   Width of the images"
echo "--height                  Height of the images"
echo "--tool_name               Tool name [MandSeg | RCSeg]"
echo "--threshold               Threshold to use to binarize scans in postprocess. (-1 for otsu | [0;255] for a specific value)"
echo "-h|--help                 Print this Help."
echo
}

while [ "$1" != "" ]; do
    case $1 in
        --dir_src )  shift
            dir_src=$1;;
        --dir_input )  shift
            dir_input=$1;;
        --dir_output )  shift
            dir_output=$1;;
        --path_model )  shift
            path_model=$1;;
        --min_percentage )  shift
            min_percentage=$1;;
        --max_percentage )  shift
            max_percentage=$1;;
        --width )  shift
            width=$1;;
        --height )  shift
            height=$1;;
        --tool_name )  shift
            tool_name=$1;;
        --threshold )  shift
            threshold=$1;;
        -h | --help )
            Help
            exit;;
        * ) 
            echo ' - Error: Unsupported flag'
            Help
            exit 1
    esac
    shift
done

dir_src="${dir_src:-./CBCT_seg/src}"
dir_input="${dir_input:-./Scans}"
dir_output="${dir_output:-$dir_input}"

min_percentage="${min_percentage:-30}"
max_percentage="${max_percentage:-90}"
width="${width:-256}"
height="${height:-256}"
tool_name="${tool_name:-MandSeg}"
threshold="${threshold:--1}"


python3 $dir_src/py/preprocess.py \
    --dir $dir_input \
    --desired_width $width \
    --desired_height $height \
    --min_percentage $min_percentage \
    --max_percentage $max_percentage \
    --out "$dir_input"_preprocessed \

python3 $dir_src/py/predict_seg.py \
    --dir_predict "$dir_input"_preprocessed \
    --load_model $path_model \
    --width $width \
    --height $height \
    --out "$dir_input"_predicted \

python3 $dir_src/py/postprocess.py \
    --dir "$dir_input"_predicted \
    --original_dir $dir_input \
    --tool $tool_name \
    --threshold $threshold \
    --out $dir_output \
