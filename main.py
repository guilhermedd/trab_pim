from segmentation import Segmentation

if __name__ == '__main__':
    segmentation = Segmentation()
    print(segmentation)
    segmentation.save_highest()
    segmentation.slice_plot()