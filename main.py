# import multiprocessing
# from PIL import Image
# from src.remove_background.remove import BackgroundRemover
# from src.image_downloader.download import image_downloader

# Uncomment to run the code
# remover = BackgroundRemover()
# input_image = np.array(Image.open("/home/xcelore/Desktop/Projects/Image-Studio/Image-Studio/src/assets/demo.jpg"))
# output_image = remover.remove_background(input_image, background_color="green")
# output_image.save("output.png")


# indian_bollywood_actors = [
#     "Shah Rukh Khan",
#     "Salman Khan",
#     "Aamir Khan",
#     "Akshay Kumar",
#     "Hrithik Roshan",
#     "Ajay Devgn",
#     "Ranbir Kapoor",
#     "Varun Dhawan",
#     "Ranveer Singh",
#     "Saif Ali Khan",
#     "Shahid Kapoor",
#     "Ayushmann Khurrana",
#     "Vicky Kaushal",
#     "Siddharth Malhotra",
#     "Kartik Aaryan",
#     "Tiger Shroff",
#     "Arjun Kapoor",
#     "John Abraham",
#     "Rajkummar Rao"
# ]
#
#
# def download_images(query_string):
#     image_downloader(
#         query=query_string,
#         limit=5,
#         output_dir='dataset',
#         adult_filter_off=True,
#         force_replace=False,
#         timeout=60,
#         filter_string="",
#         verbose=True,
#         badsites=[],
#         name='Image'
#     )
#
#
# if __name__ == "__main__":
#     workers = multiprocessing.cpu_count()//2
#     print(workers)
#     with multiprocessing.Pool(processes=workers) as pool:
#         pool.map(download_images, indian_bollywood_actors)
