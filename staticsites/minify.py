__author__ = 'Christian Bianciotto'


import csscompressor
import htmlmin
import slimit


def xml(content, comment=''):
    if comment:
        comment = '<!-- %s -->\n' % comment
    else:
        comment = ''
    return comment + htmlmin.minify(content,
                                    remove_comments=True,
                                    remove_empty_space=True,
                                    remove_all_empty_space=True,
                                    reduce_empty_attributes=False,
                                    reduce_boolean_attributes=False,
                                    remove_optional_attribute_quotes=False,
                                    keep_pre=False,
                                    pre_tags=(u'pre', u'textarea'),
                                    pre_attr='pre')


def css(content, comment=''):
    if comment:
        comment = '/* %s */\n' % comment
    else:
        comment = ''

    return comment + csscompressor.compress(content)


def js(content, comment=''):
    if comment:
        comment = '/* %s */\n' % comment
    else:
        comment = ''
    return comment + slimit.minify(content,
                                   mangle=False,
                                   mangle_toplevel=False)
