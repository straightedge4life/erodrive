let api_url = 'https://graph.microsoft.com/v1.0';
let large_file_upload_switch = true;

/**
 * get Cookie from django framework
 * @param name
 * @returns {null}
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 *
 * @param remote_path
 * @param file_name
 * @returns {string}
 */
function prepare_remote_path(remote_path, file_name){
    if (remote_path !== '/') {
         return encodeURIComponent(':' + remote_path + '/' + file_name + ':/');
    } else {
        return '';
    }
}

/**
 * Get upload session from Microsoft
 * @param access_token
 * @param remote_path
 * @param file_name
 * @returns {string}
 */
function getUploadSession(access_token, remote_path, file_name){
    remote_path = prepare_remote_path(remote_path,file_name);

    let url = api_url + '/drive/root' + remote_path + 'createUploadSession'
    let upload_session = '';
    $.ajax({
        async:false,
        url:url,
        method:'POST',
        headers:{
            'Authorization': 'bearer ' + access_token,
            'Content-Type': 'application/json'
        },
        success:function(ret){
            upload_session =  ret;
        }
    });

    return upload_session;

}

/**
 * Upload small file below 4MB.
 * @param file
 * @param remote_path
 * @param successFunc
 */
function small_file_upload(file, remote_path, successFunc, failFunc){
    remote_path = prepare_remote_path(remote_path, file.name)
    let url = api_url + '/drive/root' + remote_path + 'content'
    $.ajax({
            async: false,
            url: url,
            data: file,
            processData:false,
            method: 'PUT',
            headers: {
                'Authorization': 'bearer ' + access_token,
                'Content-Type': 'application/json'
            },
            success: function (ret) {
                successFunc(ret);
            },
            complete:function(ret){
                failFunc(ret.responseJSON);
            }
        });
}

/**
 * When file size over 4MB(4 * 1024 * 1204),it will upload file with chunk;
 * @param file
 * @param remote_path
 */
function large_file_upload(file, remote_path){
    let upload_session = getUploadSession(access_token, remote_path, file.name);
    let upload_url = upload_session.uploadUrl;
    let pointer = 0;
    let file_size = file.size;
    let step = 327680 * 32;
    let remainder = file_size % step;
    let composite_num = file_size - remainder;
    let step_num = composite_num / step;

    for (let i = 1 ; i <= step_num ; i++){


        if(!large_file_upload_switch){
            continue;
        }
        console.log('正在上传第'+i+'次... ');
        let start = pointer;
        pointer += step;
        console.log('字节范围:' + start + ' - ' + pointer);
        piece_upload(upload_url, file.slice(start, pointer), start, pointer, file_size);
        console.log('----------------------------------');
        progress_bar_fill(math.format(math.chain(math.bignumber(i)).divide(math.bignumber(step_num)).done()) * 100 - 1);

    }

    // latest pieces
    console.log('正在上传最后一次... ');
    let start = pointer;
    console.log('字节范围:' + start + ' - ' + file_size);
    piece_upload(upload_url, file.slice(start, file_size), start, file_size, file_size);
    console.log('----------------------------------');
    progress_bar_fill(100);

}

/**
 *  Upload file piece.
 * @param url
 * @param file
 * @param start
 * @param end
 * @param file_size
 */
function piece_upload(url, file, start, end, file_size){
    if(!large_file_upload_switch){
        return false;
    }
    end -=1;
    let headers = {
           'Content-Range': 'bytes '+ start +'-'+ end + '/' + file_size,
    }

    console.log('HEADERS:');
    console.log(headers);
    $.ajax({
        async:false,
        url:url,
        headers:headers,
        data:file,
        method:'PUT',
        processData:false,
        complete:function(ret){

            if(ret.responseJSON.error){
                console.log(ret.responseJSON.error);
                large_file_upload_switch = false;
            }else{
                console.log(ret);
            }
        }

    });
}

/**
 *
 * @param file
 * @param uri
 */
function upload_file(file, uri){
    let formData = new FormData();
    formData.append('file', file);
    $.ajax({
        url: uri,
        method: "POST",
        datatype: "Json",
        processData:false,
        contentType:false,
        headers:{
            'X-CSRFToken': getCookie('csrftoken')
        },
        data: formData,
        success: function (ret) {
            console.log(ret)
            upload_url = ret.uploadUrl
        }
    })


}

/**
 * Change progress bar status
 * @param percent
 * @param err_msg
 */
function progress_bar_fill(percent, err_msg = null){
    let progress_bar = $('.progress-bar');
    progress_bar.width(percent + '%');

    if (percent == 100) {
        progress_bar.html('SUCCESS');
    } else {
        progress_bar.html(percent + '%');
    }

    if (err_msg){
        progress_bar.addClass('progress-err')
        progress_bar.html(err_msg);
    }
}