from PIL import Image # pyright: ignore[reportMissingImports]

# Open the PNG icon
img = Image.open("icon.png").convert("RGBA")

# Save as ICO with multiple sizes for better scaling
img.save("app.ico", sizes=[
    (256,256),
    (128,128),
    (64,64),
    (48,48),
    (32,32),
    (16,16)
])

print("✅ app.ico created successfully!")

