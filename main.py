import zipfile


def uzip_data():
    # unzip data.zip to the folder
    zip_ref = zipfile.ZipFile("data.zip", 'r')
    zip_ref.extractall("")
    zip_ref.close()
    print("complete uzip")


def read_data():
	

def main():
    uzip_data()
    read_data()

if __name__ == "__main__":
    main()
