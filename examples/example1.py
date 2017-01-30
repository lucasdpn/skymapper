# load projection and helper functions
import numpy as np
import skymapper as skm
import matplotlib.pylab as plt

def getCatalog(size=10000):
    # dummy catalog
    ra = np.random.uniform(size=size, low=-55, high=100)
    dec = np.random.uniform(size=size, low=-65, high=-40)
    return ra, dec

def plotFootprint(ax, proj, **kwargs):
    from matplotlib.patches import Polygon
    data = np.loadtxt('des-round13-poly.txt')
    ra, dec = data[:,0], data[:,1]
    x,y  = proj(ra, dec)
    poly = Polygon(np.dstack((x,y))[0], closed=True, **kwargs)
    ax.add_artist(poly)

def plotDensity(ra, dec, nside=1024, sep=5., proj_class=skm.LambertConformalProjection, figsize=None):
    # get count in healpix cells, restrict to non-empty cells
    bc, _, _, vertices = skm.getCountAtLocations(ra, dec, nside=nside, return_vertices=True)

    # setup figure
    import matplotlib.cm as cm
    cmap = cm.YlOrRd
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, aspect='equal')

    # setup map: define AEA map optimal for given RA/Dec
    proj = skm.createConicMap(ax, ra, dec, proj_class=proj_class)

    # add lines and labels for meridians/parallels (separation 5 deg)
    meridians = np.arange(-90, 90+sep, sep)
    parallels = np.arange(0, 360+sep, sep)
    skm.setMeridianPatches(ax, proj, meridians, linestyle='-', lw=0.5, alpha=0.3, zorder=2)
    skm.setParallelPatches(ax, proj, parallels, linestyle='-', lw=0.5, alpha=0.3, zorder=2)
    skm.setMeridianLabels(ax, proj, meridians, loc="left", fmt=skm.pmDegFormatter)
    if dec.mean() > 0:
        skm.setParallelLabels(ax, proj, parallels, loc="bottom")
    else:
        skm.setParallelLabels(ax, proj, parallels, loc="top")

    # add healpix counts from vertices
    vmin, vmax = np.percentile(bc,[10,90])
    poly = skm.plotHealpixPolygons(ax, proj, vertices, color=bc, vmin=vmin, vmax=vmax, cmap=cmap, zorder=2, rasterized=True)

    # add colorbar
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="2%", pad=0.0)
    cb = fig.colorbar(poly, cax=cax)
    cb.set_label('$n_g$ [arcmin$^{-2}$]')
    cb.solids.set_edgecolor("face")

    # show (and save) ...
    fig.tight_layout()
    fig.show()
    return fig, ax, proj


if __name__ == "__main__":

    # load RA/Dec from catalog
    size = 100000
    ra, dec = getCatalog(size)

    # plot density in healpix cells
    nside = 64
    sep = 15
    fig, ax, proj = plotDensity(ra, dec, nside=nside, sep=sep)

    # add DES footprint
    plotFootprint(ax, proj, zorder=10, edgecolor='#2222B2', facecolor='None', lw=2)