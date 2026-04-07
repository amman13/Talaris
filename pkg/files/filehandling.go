package files

import (
	"os"

	"code.vikunja.io/api/pkg/config"

	"github.com/spf13/afero"
)

var fs afero.Fs
var afs *afero.Afero

func setDefaultConfig() {
	if config.FilesBasePath.GetString() != "" {
		afs.Fs = afero.NewBasePathFs(
			afs.Fs,
			config.FilesBasePath.GetString(),
		)
	}
}

func InitFileHandler() {
	fs = afero.NewOsFs()
	afs = &afero.Afero{Fs: fs}
	setDefaultConfig()
}

func FileStat(file *File) (os.FileInfo, error) {
	return afs.Stat(file.getAbsoluteFilePath())
}
