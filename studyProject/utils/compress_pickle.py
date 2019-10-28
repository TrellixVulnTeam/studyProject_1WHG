from . import studyDico
import os
import sys
import warnings
import dill 
from types import ClassType
dill._dill._reverse_typemap['ClassType'] = ClassType




_DEFAULT_EXTENSION_MAP = {
    None: ".pkl",
    "pickle": ".pkl",
    "gzip": ".gz",
    "bz2": ".bz",
    "lzma": ".lzma",
    "zipfile": ".zip",
}

_DEFAULT_COMPRESSION_WRITE_MODES = {
    None: r"wb+",
    "pickle": r"wb+",
    "gzip": r"wb",
    "bz2": r"wb",
    "lzma": r"wb",
    "zipfile": r"w",
}

_DEFAULT_COMPRESSION_READ_MODES = {
    None: r"rb+",
    "pickle": r"rb+",
    "gzip": r"rb",
    "bz2": r"rb",
    "lzma": r"rb",
    "zipfile": r"r",
}


def get_known_compressions():
    """Get a list of known compression protocols
    Returns
    -------
    compressions: list
        List of known compression protocol names.
    """
    return [c for c in _DEFAULT_EXTENSION_MAP]


def get_default_compression_mapping():
    """Get a mapping from known compression protocols to the default filename
    extensions.
    Returns
    -------
    compression_map: dict
        Dictionary that maps known compression protocol names to their default
        file extension.
    """
    return _DEFAULT_EXTENSION_MAP.copy()


def get_compression_write_mode(compression):
    """Get the compression's default mode for openning the file buffer for
    writing.
    Returns
    -------
    write_mode_map: dict
        Dictionary that maps known compression protocol names to default write
        mode used to open files for
        :func:`~compress_pickle.compress_pickle.dump`.
    """
    try:
        return _DEFAULT_COMPRESSION_WRITE_MODES[compression]
    except Exception:
        raise ValueError(
            "Unknown compression {}. Available values are: {}".format(
                compression, list(_DEFAULT_COMPRESSION_WRITE_MODES.keys())
            )
        )


def get_compression_read_mode(compression):
    """Get the compression's default mode for openning the file buffer for
    reading.
    Returns
    -------
    read_mode_map: dict
        Dictionary that maps known compression protocol names to default write
        mode used to open files for
        :func:`~compress_pickle.compress_pickle.load`.
    """
    try:
        return _DEFAULT_COMPRESSION_READ_MODES[compression]
    except Exception:
        raise ValueError(
            "Unknown compression {}. Available values are: {}".format(
                compression, list(_DEFAULT_COMPRESSION_READ_MODES.keys())
            )
        )


def set_default_extensions(filename, compression=None):
    """Set the filename's extension to the default that corresponds to
    a given compression protocol. If the filename already has a known extension
    (a default extension of a known compression protocol) it is removed
    beforehand.
    Parameters
    ----------
    filename: str
        The filename to which to set the default extension
    compression: None or str (optional)
        A compression protocol. To see the known compression protocolos, use
        :func:`~compress_pickle.compress_pickle.get_known_compressions`
    Returns
    -------
    filename: str
        The filename with the extension set to the default given by the
        compression protocol.
    Notes
    -----
    To see the mapping between known compression protocols and filename
    extensions, call the function
    :func:`~compress_pickle.compress_pickle.get_default_compression_mapping`.
    """
    default_extension = _DEFAULT_EXTENSION_MAP[compression]
    if not filename.endswith(default_extension):
        for ext in _DEFAULT_EXTENSION_MAP.values():
            if ext == default_extension:
                continue
            if filename.endswith(ext):
                filename = filename[: (len(filename) - len(ext))]
                break
        filename += default_extension
    return filename


def infer_compression_from_filename(filename, unhandled_extensions="raise"):
    """Infer the compression protocol by the filename's extension. This
    looks-up the default compression to extension mapping given by
    :func:`~compress_pickle.compress_pickle.get_default_compression_mapping`.
    Parameters
    ----------
    filename: str
        The filename for which to infer the compression protocol
    unhandled_extensions: str (optional)
        Specify what to do if the extension is not understood. Can be
        "ignore" (do nothing), "warn" (issue warning) or "raise" (raise a
        ValueError).
    Returns
    -------
    compression: str
        The inferred compression protocol's string
    Notes
    -----
    To see the mapping between known compression protocols and filename
    extensions, call the function
    :func:`~compress_pickle.compress_pickle.get_default_compression_mapping`.
    """
    if unhandled_extensions not in ["ignore", "warn", "raise"]:
        raise ValueError(
            "Unknown 'unhandled_extensions' value {}. Allowed values are "
            "'ignore', 'warn' or 'raise'".format(unhandled_extensions)
        )
    extension = os.path.splitext(filename)[1]
    compression = None
    for comp, ext in _DEFAULT_EXTENSION_MAP.items():
        if comp is None:
            continue
        if ext == extension:
            compression = comp
            break
    if compression is None and extension != ".pkl":
        if unhandled_extensions == "raise":
            raise ValueError(
                "Cannot infer compression protocol from filename {} "
                "with extension {}".format(filename, extension)
            )
        elif unhandled_extensions == "warn":
            warnings.warn(
                "Cannot infer compression protocol from filename {} "
                "with extension {}".format(filename, extension),
                category=RuntimeWarning,
            )
    return compression


def compress_pickle_dump(
    obj,
    path,
    compression="infer",
    mode=None,
    protocol=-1,
    fix_imports=True,
    unhandled_extensions="raise",
    set_default_extension=True,
    **kwargs
):
    r"""Dump the contents of an object to disk, to the supplied path, using a
    given compression protocol.
    For example, if ``gzip`` compression is specified, the file buffer is
    opened as ``gzip.open`` and the desired content is dumped into the buffer
    using a normal ``pickle.dump`` call.
    Parameters
    ----------
    obj: any
        The object that will be saved to disk
    path: str
        The path to the file to which to dump ``obj``
    compression: None or str (optional)
        The compression protocol to use. By default, the compression is
        inferred from the path's extension. To see available compression
        protocols refer to
        :func:`~compress_pickle.compress_pickle.get_known_compressions`.
    mode: None or str (optional)
        Mode with which to open the file buffer. The default changes according
        to the compression protocol. Refer to
        :func:`~compress_pickle.compress_pickle.get_compression_write_mode` to
        see the defaults.
    protocol: int (optional)
        Pickle protocol to use
    fix_imports: bool (optional)
        If ``fix_imports`` is ``True`` and ``protocol`` is less than 3, pickle
        will try to map the new Python 3 names to the old module names used
        in Python 2, so that the pickle data stream is readable with Python 2.
    set_default_extension: bool (optional)
        If ``True``, the default extension given the provided compression
        protocol is set to the supplied ``path``. Refer to
        :func:`~compress_pickle.compress_pickle.set_default_extensions` for
        more information.
    unhandled_extensions: str (optional)
        Specify what to do if the extension is not understood when inferring
        the compression protocol from the provided path. Can be "ignore" (use
        ".pkl"), "warn" (issue warning and use ".pkl") or "raise" (raise a
        ValueError).
    kwargs:
        Any extra keyword arguments are passed to the compressed file opening
        protocol.
    Notes
    -----
    To see the mapping between known compression protocols and filename
    extensions, call the function
    :func:`~compress_pickle.compress_pickle.get_default_compression_mapping`.
    """
    if compression == "infer":
        compression = infer_compression_from_filename(path, unhandled_extensions)
    if set_default_extension:
        path = set_default_extensions(path, compression=compression)
    arch = None
    if mode is None:
        mode = get_compression_write_mode(compression)
    if compression is None or compression == "pickle":
        file = open(path, mode=mode)
    elif compression == "gzip":
        import gzip

        file = gzip.open(path, mode=mode, **kwargs)
    elif compression == "bz2":
        import bz2

        file = bz2.open(path, mode=mode, **kwargs)
    elif compression == "lzma":
        import lzma

        file = lzma.open(path, mode=mode, **kwargs)
    elif compression == "zipfile":
        import zipfile

        arch = zipfile.ZipFile(path, mode=mode, **kwargs)
        if sys.version_info < (3, 6):
            arcname = os.path.basename(path)
            arch.write(path, arcname=arcname)
        else:
            file = arch.open(path, mode=mode)
    if arch is not None:
        with arch:
            if sys.version_info < (3, 6):
                buff = dill.dumps(obj, protocol=protocol)
                arch.writestr(arcname, buff)
            else:
                with file:
                    dill.dump(obj, file, protocol=protocol)
    else:
        with file:
            dill.dump(obj, file, protocol=protocol)


def compress_pickle_load(
    path,
    compression="infer",
    mode=None,
    fix_imports=True,
    encoding="ASCII",
    errors="strict",
    set_default_extension=True,
    unhandled_extensions="raise",
    **kwargs
):
    r"""Load an object from a file stored in disk, given compression protocol.
    For example, if ``gzip`` compression is specified, the file buffer is opened
    as ``gzip.open`` and the desired content is loaded from the open buffer
    using a normal ``pickle.load`` call.
    Parameters
    ----------
    path: str
        The path to the file from which to load the ``obj``
    compression: None or str (optional)
        The compression protocol to use. By default, the compression is
        inferred from the path's extension. To see available compression
        protocols refer to
        :func:`~compress_pickle.compress_pickle.get_known_compressions`.
    mode: None or str (optional)
        Mode with which to open the file buffer. The default changes according
        to the compression protocol. Refer to
        :func:`~compress_pickle.compress_pickle.get_compression_read_mode` to
        see the defaults.
    fix_imports: bool (optional)
        If ``fix_imports`` is ``True`` and ``protocol`` is less than 3, pickle
        will try to map the new Python 3 names to the old module names used
        in Python 2, so that the pickle data stream is readable with Python 2.
    encoding: str (optional)
        Tells pickle how to decode 8-bit string instances pickled by Python 2.
        Refer to the standard ``pickle`` documentation for details.
    errors: str (optional)
        Tells pickle how to decode 8-bit string instances pickled by Python 2.
        Refer to the standard ``pickle`` documentation for details.
    set_default_extension: bool (optional)
        If `True`, the default extension given the provided compression
        protocol is set to the supplied `path`. Refer to
        :func:`~compress_pickle.compress_pickle.set_default_extensions` for
        more information.
    unhandled_extensions: str (optional)
        Specify what to do if the extension is not understood when inferring
        the compression protocol from the provided path. Can be "ignore" (use
        ".pkl"), "warn" (issue warning and use ".pkl") or "raise" (raise a
        ValueError).
    kwargs:
        Any extra keyword arguments are passed to the compressed file opening
        protocol.
    Returns
    -------
    The unpickled object: any
    Notes
    -----
    To see the mapping between known compression protocols and filename
    extensions, call the function
    :func:`~compress_pickle.compress_pickle.get_default_compression_mapping`.
    """
    if compression == "infer":
        compression = infer_compression_from_filename(path, unhandled_extensions)
    if set_default_extension:
        path = set_default_extensions(path, compression=compression)
    if mode is None:
        mode = get_compression_read_mode(compression)
    arch = None
    if compression is None or compression == "pickle":
        file = open(path, mode=mode)
    elif compression == "gzip":
        import gzip

        file = gzip.open(path, mode=mode, **kwargs)
    elif compression == "bz2":
        import bz2

        file = bz2.open(path, mode=mode, **kwargs)
    elif compression == "lzma":
        import lzma
        # print("jeds")
        file = lzma.open(path, mode=mode, **kwargs)
        # print("ici")
    elif compression == "zipfile":
        import zipfile

        arch = zipfile.ZipFile(path, mode=mode, **kwargs)
        file = arch.open(path, mode=mode)
    if arch is not None:
        with arch:
            with file:
                output = dill.load(
                    file
                )
    else:
        with file:
            # print("iid")
            output = dill.load(
                file
            )
    # print(type(output))
    return output
compress_pickle=studyDico(dict(load=compress_pickle_load,dump=compress_pickle_dump))
