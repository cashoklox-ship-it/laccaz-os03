var desktopsList = desktops();
for (var i = 0; i < desktopsList.length; i++) {
 var d = desktopsList[i];
 d.wallpaperPlugin = "org.kde.image";
 d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
 d.writeConfig("Image", "file:///usr/share/wallpapers/Laccaz/contents/images/3840x2160.png");
}
